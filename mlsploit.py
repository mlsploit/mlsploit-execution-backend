import glob
import json
import os
import shutil
import tempfile
import time
from urllib.request import urlretrieve

from celery import Celery
from celery.signals import celeryd_after_setup
import docker
from git import Git

from api import File, Job, Module, RestClient, User
from constants import *


app = Celery(APP_NAME, broker=BROKER_URL, backend=BACKEND_URL)
app.conf.update(worker_prefetch_multiplier=1, worker_send_task_events=True)
app.conf.beat_schedule = {
    "fetch-jobs-every-10-seconds": {
        "task": "mlsploit.fetch_actionable_jobs",
        "options": {"queue": "housekeeping"},
        "schedule": 10.0,
    }
}

RestClient.set_token(API_ADMIN_TOKEN)


@celeryd_after_setup.connect
def setup_docker_images(sender, instance, **kwargs):
    client = docker.from_env()

    modules, num_built = Module.get_all(), 0
    for module in modules:
        name = module.name

        if "*" in BUILD_MODULES or name in BUILD_MODULES:
            repo = module.repo
            tmp_dir = tempfile.mkdtemp()

            print(f"Building docker image for {name}...")

            try:
                Git(tmp_dir).clone(repo)
                repo_dir = glob.glob(os.path.join(tmp_dir, "*"))[0]

                client.images.build(path=repo_dir, tag=name)
                num_built += 1

                print(f"Successfully built docker image for {name}.")

            except Exception as e:
                print(f"[ERROR] Failed to build docker image for {name} ({e})")

            shutil.rmtree(tmp_dir)
    print(f"Built docker images for {num_built} modules.")

    wait = 10
    print(f"Waiting {wait}s for networking services to spin up...")
    time.sleep(wait)


@app.task
def fetch_actionable_jobs():
    jobs = Job.get_all_actionable()

    for job in jobs:
        job_module = job.task.function.module.name
        job.status = "QUEUED"
        promise = perform_job.s(job.id)
        promise.apply_async(queue=job_module)

    return [job.url for job in jobs]


@app.task(bind=True)
def perform_job(self, job_id):
    job = Job.from_id(job_id)
    job.status = "RUNNING"

    output_json, output_file_names = dict(), list()

    # Get all data from API at once since it is time-cached
    current_user = User.get_current()
    current_user_url = current_user.url if current_user is not None else None
    job_url = job.url
    module = job.task.function.module
    module_name = module.name
    function_name = job.task.function.name
    arguments = job.task.arguments
    owner_url = job.owner.url
    parent_job = job.parent_job
    input_files = job.run.files if parent_job is None else parent_job.output_files
    input_file_names = [f.name for f in input_files]
    input_file_tags = {f.name: f.tags for f in input_files}
    input_file_urls = {f.name: f.url for f in input_files}
    input_file_blob_urls = {f.name: f.blob_url for f in input_files}

    # Create job folder with input and output directories
    job_dir = os.path.join(SCRATCH_DIR, "jobs", str(job_id))
    input_dir = os.path.join(job_dir, "input")
    output_dir = os.path.join(job_dir, "output")
    job_dir_docker = os.path.join(SCRATCH_DIR_DOCKER, "jobs", str(job_id))
    input_dir_docker = os.path.join(job_dir_docker, "input")
    output_dir_docker = os.path.join(job_dir_docker, "output")

    original_umask = os.umask(0)
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.umask(original_umask)

    # Download input files
    for name, url in input_file_blob_urls.items():
        urlretrieve(url, os.path.join(input_dir, name))

    # Create input JSON file
    input_json_dict = {
        "name": function_name,
        "num_files": len(input_file_names),
        "files": input_file_names,
        "options": arguments,
        "tags": [input_file_tags[name] for name in input_file_names],
    }
    input_json_filepath = os.path.join(input_dir, "input.json")
    with open(input_json_filepath, "w") as f:
        json.dump(input_json_dict, f)

    # Run docker image
    container_logs = ""
    client = docker.from_env()
    try:
        container = client.containers.run(
            "%s:latest" % module_name,
            environment=["PYTHONUNBUFFERED=1"],
            auto_remove=True,
            detach=True,
            stdout=True,
            stderr=True,
            volumes={
                input_dir_docker: {"bind": "/mnt/input", "mode": "rw"},
                output_dir_docker: {"bind": "/mnt/output", "mode": "rw"},
            },
        )

        for line in container.logs(stream=True):
            container_logs += line.decode("utf-8")
            job.logs = container_logs

    except Exception as e:
        print("[MLSPLOIT-DOCKER-ERROR] %s" % e)
        job.status = "FAILED"

    else:
        container_exit_status = container.wait()
        container_exit_status = container_exit_status["StatusCode"]

        if container_exit_status == 0:
            # Update output for job
            output_json_filepath = os.path.join(output_dir, "output.json")
            with open(output_json_filepath, "r") as f:
                output_json = json.load(f)
            job.output = output_json

            # Upload output files
            output_file_names = output_json["files"]
            output_file_tags = output_json["tags"]
            output_filepaths = [os.path.join(output_dir, f) for f in output_file_names]
            assert all(os.path.exists(fp) for fp in output_filepaths)
            output_file_urls = list()
            for name, tags, path in zip(
                output_file_names, output_file_tags, output_filepaths
            ):

                f = None
                file_kwargs = {"kind": "OUTPUT", "tags": tags, "blob": open(path, "rb")}
                if current_user_url != owner_url:
                    file_kwargs["owner"] = owner_url

                if name in output_json["files_modified"]:
                    file_kwargs["parent_file"] = input_file_urls[name]
                    f = File.create(**file_kwargs)

                elif name in output_json["files_created"]:
                    f = File.create(**file_kwargs)

                elif name in input_file_names:
                    file_url = input_file_urls[name]
                    file_tags = input_file_tags[name]
                    file_tags.update(tags)
                    f = File(file_url)
                    f.tags = file_tags

                if f is not None:
                    output_file_urls.append(f.url)

            job.output_files = output_file_urls
            job.status = "FINISHED"

        else:
            job.status = "FAILED"

    finally:
        # Update logs
        job.logs = container_logs

        # Cleanup
        shutil.rmtree(job_dir)

    return job_url, output_json, output_file_names

# Execution Orchestrator for MLsploit

## ENVIRONMENT SETUP

The primary configuration settings of the execution module are stored 
inside the `.env` file, which you'll need to modify
according to your needs.

The first thing you should update is the `MLSPLOIT_API_ADMIN_TOKEN`, 
which is necessary for accessing the data API for MLsploit.

## RUN WITH DOCKER

We use `docker-compose` to orchestrate the setup and execution of the service.
You only need to setup `docker` on your system and then run the following command:

```bash
$ bash docker-start-master.sh
```

This starts the execution service in *MASTER* mode. 
The *MASTER* mode of the execution service runs the 
scheduling, networking, monitoring and execution of the jobs.
The *WORKER* mode, which only handles the execution of the jobs,
can be run in parallel on another system using the following command:

```bash
$ bash docker-start-worker.sh
```

For the *WORKER* mode, you will need to update the host environment variables in the `.env` file
to point to the *MASTER* node.

## MANUAL SETUP

### Install the dependencies

```bash
$ pip install -r requirements.txt
```


### Set up the environment

```bash
$ export MLSPLOIT_BROKER_URL='amqp://admin:password@localhost:5672/mlsploit'
$ export MLSPLOIT_BACKEND_URL='redis://localhost:6379'
$ export MLSPLOIT_API_ADMIN_TOKEN=<token here>
```

## USAGE

```bash
$ celery worker -A mlsploit -B \
    -l info \
    -Ofair \
    -c 5
```

The `-B` flag should be enabled only on one node worker since it queues the pending jobs.

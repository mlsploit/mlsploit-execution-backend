import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH_DIR = os.path.join(BASE_DIR, ".scratch")
BASE_DIR_DOCKER = os.getenv("MLSPLOIT_DOCKER_HOST_BASE_DIR") or BASE_DIR
SCRATCH_DIR_DOCKER = os.path.join(BASE_DIR_DOCKER, ".scratch")
os.makedirs(SCRATCH_DIR, exist_ok=True)

APP_NAME = "mlsploit"

BROKER_URL = os.getenv("MLSPLOIT_BROKER_URL")
assert BROKER_URL, """
    MLSPLOIT_BROKER_URL environment variable not found.
    $ export MLSPLOIT_BROKER_URL='amqp://admin:password@localhost:5672/mlsploit'
    """

BACKEND_URL = os.getenv("MLSPLOIT_BACKEND_URL")
assert BACKEND_URL, """
    MLSPLOIT_BACKEND_URL environment variable not found.
    $ export MLSPLOIT_BACKEND_URL='redis://localhost:6379'
    """

API_ADMIN_TOKEN = os.getenv("MLSPLOIT_API_ADMIN_TOKEN")
assert API_ADMIN_TOKEN, """
    MLSPLOIT_API_ADMIN_TOKEN environment variable not found.
    $ export MLSPLOIT_API_ADMIN_TOKEN='dd6f003f47b68e3fcd24fe5b3cade72168557d9f'
    """

EXECUTION_MODE = os.getenv("CONTAINER_BUILD_STAGE")

BUILD_MODULES = os.getenv("MLSPLOIT_BUILD_MODULES")
BUILD_MODULES = (BUILD_MODULES or "").split(",")

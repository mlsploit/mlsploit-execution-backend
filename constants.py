import os as _os


BASE_DIR = _os.path.dirname(_os.path.abspath(__file__))
SCRATCH_DIR = _os.path.join(BASE_DIR, ".scratch")
BASE_DIR_DOCKER = _os.getenv("MLSPLOIT_DOCKER_HOST_BASE_DIR") or BASE_DIR
SCRATCH_DIR_DOCKER = _os.path.join(BASE_DIR_DOCKER, ".scratch")
_os.makedirs(SCRATCH_DIR, exist_ok=True)

APP_NAME = "mlsploit"

BROKER_URL = _os.getenv("MLSPLOIT_BROKER_URL")
assert (
    BROKER_URL is not None
), """
    MLSPLOIT_BROKER_URL environment variable not found.
    $ export MLSPLOIT_BROKER_URL='amqp://admin:password@localhost:5672/mlsploit'
    """

BACKEND_URL = _os.getenv("MLSPLOIT_BACKEND_URL")
assert (
    BACKEND_URL is not None
), """
    MLSPLOIT_BACKEND_URL environment variable not found.
    $ export MLSPLOIT_BACKEND_URL='redis://localhost:6379'
    """

API_ADMIN_TOKEN = _os.getenv("MLSPLOIT_API_ADMIN_TOKEN")
assert (
    API_ADMIN_TOKEN is not None
), """
    MLSPLOIT_API_ADMIN_TOKEN environment variable not found.
    $ export MLSPLOIT_API_ADMIN_TOKEN='dd6f003f47b68e3fcd24fe5b3cade72168557d9f'
    """

BUILD_MODULES = _os.getenv("MLSPLOIT_BUILD_MODULES")
BUILD_MODULES = (BUILD_MODULES or "*").split(",")

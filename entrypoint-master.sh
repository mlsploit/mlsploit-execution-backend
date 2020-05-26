#!/usr/bin/env sh

set -a && . .env && set +a

if [[ -z "${MLSPLOIT_API_ADMIN_TOKEN}" ]]
then
    echo "[ERROR] MLSPLOIT_API_ADMIN_TOKEN is not set"
    exit 1
fi

./wait-for-rabbitmq.py || exit 1

cd ./src

CELERY_ID=mlsploit.master@%h

celery worker -A mlsploit -B \
      -l info \
      -Ofair \
      -n ${CELERY_ID} \
      -Q housekeeping \
      -c ${MLSPLOIT_EXECUTION_JOB_CONCURRENCY}

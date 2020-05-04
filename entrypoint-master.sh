#!/usr/bin/env bash

set -a && . .env && set +a

if [[ -z "${MLSPLOIT_API_ADMIN_TOKEN}" ]]
then
    echo "[ERROR] MLSPLOIT_API_ADMIN_TOKEN is not set"
    exit 1
fi

cd ./src

CELERY_ID=mlsploit.master@%h

celery worker -A mlsploit -B \
      -Q housekeeping \
      -l info \
      -Ofair \
      -n ${CELERY_ID} \
      -c ${MLSPLOIT_EXECUTION_JOB_CONCURRENCY}

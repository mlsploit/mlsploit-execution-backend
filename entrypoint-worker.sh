#!/usr/bin/env bash

set -a && . .env && set +a

if [[ -z "${MLSPLOIT_API_ADMIN_TOKEN}" ]]
then
    echo "[ERROR] MLSPLOIT_API_ADMIN_TOKEN is not set"
    exit 1
fi

celery worker -A mlsploit \
      -l info \
      -Ofair \
      -c ${MLSPLOIT_EXECUTION_JOB_CONCURRENCY}

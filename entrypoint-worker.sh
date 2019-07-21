#!/usr/bin/env bash

set -a && . .env && set +a

if [[ -z "${MLSPLOIT_API_ADMIN_TOKEN}" ]]
then
    echo "[ERROR] MLSPLOIT_API_ADMIN_TOKEN is not set"
    exit 1
fi

if [[ -z "${MLSPLOIT_EXECUTION_QUEUES}" ]]
then
    MLSPLOIT_EXECUTION_QUEUES="celery"
fi

celery worker -A mlsploit \
      -Q ${MLSPLOIT_EXECUTION_QUEUES} \
      -l info \
      -Ofair \
      -c ${MLSPLOIT_EXECUTION_JOB_CONCURRENCY}

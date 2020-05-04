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

cd ./src

DATE_STR=$(date +%s)
RAND_STR=$(python3 -c "from __future__ import print_function; from coolname import generate_slug; print(generate_slug(2))")
CELERY_ID=mlsploit.worker.${DATE_STR}.${RAND_STR}@%h

celery worker -A mlsploit \
      -Q ${MLSPLOIT_EXECUTION_QUEUES} \
      -l info \
      -Ofair \
      -n ${CELERY_ID} \
      -c ${MLSPLOIT_EXECUTION_JOB_CONCURRENCY}

#!/usr/bin/env sh

set -a && . .env && set +a

if [[ -z "${MLSPLOIT_API_ADMIN_TOKEN}" ]]
then
    echo "[ERROR] MLSPLOIT_API_ADMIN_TOKEN is not set"
    exit 1
fi

export MLSPLOIT_MODULES=$(./get-module-names.sh)

./wait-for-rabbitmq.py || exit 1

cd ./src

DATE_STR=$(date +%s)
RAND_STR=$(python3 -c "from __future__ import print_function; from coolname import generate_slug; print(generate_slug(2))")
CELERY_ID=mlsploit.worker.${DATE_STR}.${RAND_STR}@%h

celery worker -A mlsploit \
      -Ofair \
      -l info \
      -n ${CELERY_ID} \
      -Q ${MLSPLOIT_MODULES:-celery} \
      -c ${MLSPLOIT_EXECUTION_JOB_CONCURRENCY}

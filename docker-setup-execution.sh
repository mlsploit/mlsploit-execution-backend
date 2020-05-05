#!/usr/bin/env bash

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd -P)"

if [[ ! -f .env ]]; then
    cp .env.example .env
fi

MASTER_DOCKER_PROJECT_NAME=mlsploit-execution-backend-master
WORKER_DOCKER_PROJECT_NAME=mlsploit-execution-backend-worker

docker-compose \
    -p ${MASTER_DOCKER_PROJECT_NAME} \
    -f docker-compose.execution.yml \
    -f docker-compose.networking.yml \
    build \
    --build-arg STAGE=master

docker-compose \
    -p ${WORKER_DOCKER_PROJECT_NAME} \
    -f docker-compose.execution.yml \
    build \
    --build-arg STAGE=worker

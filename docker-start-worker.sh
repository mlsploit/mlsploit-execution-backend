#!/usr/bin/env bash

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd -P)"

DOCKER_PROJECT_NAME=mlsploit-execution-backend-worker

docker-compose \
    -p ${DOCKER_PROJECT_NAME} \
    -f docker-compose.execution.yml \
    up

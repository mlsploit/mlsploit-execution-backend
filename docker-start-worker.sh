#!/usr/bin/env bash

set -a && . .env && set +a

MLSPLOIT_DOCKER_HOST_BASE_DIR="$(pwd)";

DOCKER_PROJECT_NAME=mlsploit-execution-backend-worker

docker-compose \
    -p ${DOCKER_PROJECT_NAME} \
    -f services.docker-compose.execution.yml \
    build \
    --build-arg STAGE=worker \
    --build-arg BASE_DIR="${MLSPLOIT_DOCKER_HOST_BASE_DIR}"

docker-compose \
    -p ${DOCKER_PROJECT_NAME} \
    -f services.docker-compose.execution.yml \
    up

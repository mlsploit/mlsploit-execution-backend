#!/usr/bin/env bash

set -a && . .env && set +a

MLSPLOIT_DOCKER_HOST_BASE_DIR="$(pwd)";

docker-compose \
    -f services.docker-compose.execution.yml \
    -f services.docker-compose.networking.yml \
    build \
    --build-arg STAGE=master \
    --build-arg BASE_DIR="${MLSPLOIT_DOCKER_HOST_BASE_DIR}"

docker-compose \
    -f services.docker-compose.execution.yml \
    -f services.docker-compose.networking.yml \
    up

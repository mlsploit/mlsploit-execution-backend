#!/usr/bin/env bash

set -a && . .env && set +a

MLSPLOIT_DOCKER_HOST_BASE_DIR="$(pwd)";
MLSPLOIT_HOST_URL=$(aws dynamodb get-item --table-name mlsploit --key '{"name": {"S": "host-ip"}}' | jq -r '.Item.value.S')
MLSPLOIT_API_ADMIN_TOKEN=$(aws dynamodb get-item --table-name mlsploit --key '{"name": {"S": "admin-token"}}' | jq -r '.Item.value.S')

docker-compose \
    -f services.docker-compose.execution.yml \
    build \
    --build-arg STAGE=worker \
    --build-arg MLSPLOIT_HOST_URL=${MLSPLOIT_HOST_URL} \
    --build-arg BASE_DIR="${MLSPLOIT_DOCKER_HOST_BASE_DIR}" \
    --build-arg MLSPLOIT_API_ADMIN_TOKEN=${MLSPLOIT_API_ADMIN_TOKEN}

docker-compose \
    -f services.docker-compose.execution.yml \
    up

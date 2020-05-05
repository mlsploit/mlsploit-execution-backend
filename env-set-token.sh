#!/usr/bin/env bash

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd -P)"

if [[ ! -f .env ]]; then
    cp .env.example .env
fi

function usage() {
    echo "usage: bash env-set-token.sh <MLSPLOIT_API_ADMIN_TOKEN>"
}

function update_env() {
    KEY="$1"; VAL="$2"; LINE_NUM=$(grep -nm 1 "^${KEY}=" .env | cut -f1 -d:)
    (sed "${LINE_NUM}s/.*/${KEY}=${VAL}/" .env > .env.tmp) && mv .env.tmp .env
}

if [[ -z $1 ]]; then
    usage
    exit 1
fi

MLSPLOIT_API_ADMIN_TOKEN="$1"
update_env MLSPLOIT_API_ADMIN_TOKEN "$MLSPLOIT_API_ADMIN_TOKEN"

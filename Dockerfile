FROM docker:stable

VOLUME /app

ENV PYTHONUNBUFFERED 1

RUN apk upgrade --no-cache \
    && apk add --no-cache --update git python3

COPY requirements.txt /
RUN pip3 install --upgrade pip \
    && pip install -r /requirements.txt \
    && rm -rf /root/.cache/pip/wheels/*

WORKDIR /app

ARG STAGE
ARG BASE_DIR
ARG MLSPLOIT_HOST_URL
ARG MLSPLOIT_API_ADMIN_TOKEN
ENV CONTAINER_BUILD_STAGE=$STAGE
ENV MLSPLOIT_HOST_URL=$MLSPLOIT_HOST_URL
ENV MLSPLOIT_DOCKER_HOST_BASE_DIR=$BASE_DIR
ENV MLSPLOIT_API_ADMIN_TOKEN=$MLSPLOIT_API_ADMIN_TOKEN

ENTRYPOINT sh entrypoint-${CONTAINER_BUILD_STAGE}.sh

FROM docker:stable

VOLUME /app

RUN apk upgrade --no-cache \
    && apk add --no-cache --update git python3 py-pip

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /
RUN pip3 install --upgrade pip \
    && pip install -r /requirements.txt \
    && rm -rf /root/.cache/pip/wheels/*

ARG STAGE
ARG BASE_DIR
ENV CONTAINER_BUILD_STAGE=$STAGE
ENV MLSPLOIT_DOCKER_HOST_BASE_DIR=$BASE_DIR

WORKDIR /app

ENTRYPOINT sh entrypoint-${CONTAINER_BUILD_STAGE}.sh

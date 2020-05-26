#!/usr/bin/env python3

import os
import re
import time

import pika


MLSPLOIT_BROKER_URL = os.getenv("MLSPLOIT_BROKER_URL")

username, password, host, port, vhost = re.search(
    r"^amqp:\/\/(\w+):([\s\S]+)@([-\w\d]+):(\d+)\/(\w+)$", MLSPLOIT_BROKER_URL
).groups()

credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, port, vhost, credentials)

wait = 5
start = time.time()
while True:
    print(f"Waiting {wait}s for RabbitMQ to come up at {host}:{port}/{vhost}")
    time.sleep(wait)

    try:
        pika.BlockingConnection(parameters)
        break
    except pika.exceptions.AMQPConnectionError:
        pass
    else:
        end = time.time()
        print(f"RabbitMQ came up in ~{round(end - start)}s")

#!/usr/bin/env python3

import os
import re
import time

import pika


MLSPLOIT_BROKER_URL = os.getenv("MLSPLOIT_BROKER_URL")
parameters = pika.URLParameters(MLSPLOIT_BROKER_URL)

wait = 5
start = time.time()
while True:
    print(f"Waiting {wait}s for RabbitMQ to come up...")
    time.sleep(wait)

    try:
        pika.BlockingConnection(parameters)
        break
    except pika.exceptions.AMQPConnectionError:
        pass
    else:
        end = time.time()
        print(f"RabbitMQ came up in ~{round(end - start)}s")

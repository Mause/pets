import json
import logging
import os
import pickle
import time
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from datetime import datetime
from os.path import dirname

import requests
import schedule
import sentry_sdk
from flask import render_template
from requests import Session
from sentry_sdk import capture_exception, push_scope
from tqdm import tqdm

from config import config
from main import app, redis
from sources import sources

if 'SENTRY_DSN' in os.environ:
    sentry_sdk.init(dsn=os.environ['SENTRY_DSN'])


EXECUTOR = PoolExecutor()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

HERE = dirname(__file__)


def update_data():
    start = time.time()
    logging.info("Starting data update")

    data, errors = get_data()

    statuses = {source: not error for source, error in errors.items()}

    data = pickle.dumps(data)
    statuses = json.dumps(statuses)

    (redis.pipeline().set("data", data).set('statuses', statuses).execute())

    for source, error in errors.items():
        if not error:
            continue

        with push_scope() as scope:
            scope.set_tag('source', source)
            capture_exception(error, scope)

    redis.set('last_updated', datetime.now().isoformat())
    logging.info("Update took %s seconds", time.time() - start)


def reliable(errors):
    # call with list() to ensure they start in parallel
    fs = [EXECUTOR.submit(s, Session()) for s in sources]

    for source, future in zip(sources, fs):
        try:
            yield from future.result()
        except Exception as e:
            logging.exception('failed to retrieve data for %s', source.__name__)
            errors[source.__name__] = e


def get_data():
    errors = {src.__name__: None for src in sources}

    data = reliable(errors)
    data = sorted(tqdm(data), key=lambda item: item.found_on, reverse=True)

    return data, errors


if __name__ == "__main__":
    update_data()

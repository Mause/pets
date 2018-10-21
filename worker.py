import time
import json
import pickle
import logging
import traceback
from itertools import chain
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor as PoolExectutor

import schedule
import requests
from tqdm import tqdm
from flask import render_template

from main import redis, app
from config import config
from sources import sources

EXECUTOR = PoolExectutor()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

MAILGUN_API_KEY = config["MAILGUN_API_KEY"]
MAILGUN_DOMAIN = config["MAILGUN_DOMAIN"]
MESSAGES_URL = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"

session = requests.Session()
session.auth = ("api", MAILGUN_API_KEY)


def send_email(subject, body):
    r = session.post(
        MESSAGES_URL,
        data={
            "to": "me@mause.me",
            "from": '"Pets Alerts" <me@mause.me>',
            "subject": subject,
            "html": body
        },
    )
    if not r.ok:
        print(r.text)
    r.raise_for_status()


def alert_error(source, error: Exception):
    tb = '\n'.join(traceback.format_tb(error.__traceback__))

    with app.app_context():
        body = render_template(
            "alert_email.html",
            source=source,
            tb=tb
        )

    send_email(f"{source} is failing", body)


def update_data():
    start = time.time()
    logging.info("Starting data update")

    data, errors = get_data()

    statuses = {source: not error for source, error in errors.items()}

    data = pickle.dumps(data)
    statuses = json.dumps(statuses)

    (
        redis
            .pipeline()
            .set("data", data)
            .set('statuses', statuses)
            .execute()
    )

    for source, error in errors.items():
        if not error:
            continue

        alert_error(source, error)

    redis.set('last_updated', datetime.now().isoformat())
    logging.info("Update took %s seconds", time.time() - start)


def reliable(errors):
    # call with list() to ensure they start in parallel
    fs = list(map(EXECUTOR.submit, sources))

    for source, future in zip(sources, fs):
        try:
            yield from future.result()
        except Exception as e:
            logging.exception(
                'failed to retrieve data for %s',
                source.__name__
            )
            errors[source.__name__] = e


def get_data():
    errors = {src.__name__: None for src in sources}

    data = reliable(errors)
    data = sorted(
        tqdm(data),
        key=lambda item: item.found_on,
        reverse=True
    )

    return data, errors


if __name__ == "__main__":
    schedule.every(5).minutes.do(update_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

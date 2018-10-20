import time
import json
import pickle
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor as PoolExectutor

import schedule
from tqdm import tqdm

from main import redis
from sources import sources

EXECUTOR = PoolExectutor()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

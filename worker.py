import time
import json
import pickle
import logging
from tqdm import tqdm
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor as PoolExectutor

import schedule

from main import redis
from sources import sources

EXECUTOR = PoolExectutor()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def update_data():
    start = time.time()
    logging.info("Starting data update")

    data, statuses = get_data()

    daata = pickle.dumps(data)
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


def reliable(statuses):
    # call with list() to ensure they start in parallel
    fs = list(map(EXECUTOR.submit, sources))

    for source, future in zip(sources, fs):
        try:
            yield from future.result()
        except Exception:
            logging.exception(
                'failed to retrieve data for %s',
                source.__name__
            )
            statuses[source.__name__] = False



def get_data():
    statuses = {src.__name__: True for src in sources}

    data = reliable(statuses)
    data = sorted(
        tqdm(data),
        key=lambda item: item.found_on,
        reverse=True
    )

    return data, statuses


if __name__ == "__main__":
    schedule.every(5).minutes.do(update_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

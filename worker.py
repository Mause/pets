import time
import pickle
import logging

import schedule

from main import get_data, redis

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def update_data():
    start = time.time()
    logging.info("Starting data update")
    redis.put("data", pickle.dumps(get_data()))
    logging.info("Update took %s seconds", time.time() - start)


if __name__ == "__main__":
    schedule.every(5).minutes.do(update_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

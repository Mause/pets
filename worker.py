import time
import pickle
import logging
from datetime import datetime

import schedule

from main import get_data, redis

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def update_data():
    start = time.time()
    logging.info("Starting data update")
    redis.set("data", pickle.dumps(get_data()))
    redis.set('last_updated', datetime.now().isoformat())
    logging.info("Update took %s seconds", time.time() - start)


if __name__ == "__main__":
    schedule.every(5).minutes.do(update_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

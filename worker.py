import time
import pickle
import logging
import crython

from main import get_data, redis


@crython.job(minute="*/5")
def update_data():
    start = time.time()
    logging.info("Starting data update")
    redis.put("data", pickle.dumps(get_data()))
    logging.info("Update took %s seconds", time.time() - start)


if __name__ == "__main__":
    crython.start()

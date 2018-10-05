import os
import pickle
import logging
from itertools import chain
from concurrent.futures import ThreadPoolExecutor as PoolExectutor

import arrow
from tqdm import tqdm
from redis import StrictRedis
from flask import Flask, render_template, jsonify, request

from sources import sources, default

logging.basicConfig(level=logging.DEBUG)

redis = StrictRedis.from_url(os.environ.get("REDIS_URL"))

EXECUTOR = PoolExectutor()
app = Flask(__name__)
app.json_encoder.default = lambda self, obj: default(obj)


def reliable():
    # call with list() to ensure they start in parallel
    fs = list(map(EXECUTOR.submit, sources))

    statuses = {src.__name__: True for src in sources}

    for source, future in zip(sources, fs):
        try:
            yield from future.result()
        except Exception:
            logging.exception(
                'failed to retrieve data for %s',
                source.__name__
            )
            statuses[source.__name__] = False

    redis.put('statuses', json.dumps(statuses))


def get_data():
    return sorted(
        tqdm(reliable()),
        key=lambda item: item.found_on,
        reverse=True
    )


def get_cached_data():
    data = pickle.loads(redis.get('data'))
    date = request.args.get('date')
    if date:
        if date == 'today':
            date = arrow.get()
        else:
            date = arrow.get(date)
        date = date.date()
        data = [pet for pet in data if pet.found_on.date() == date]
    return data


@app.route('/index.json')
def index_json():
    data = get_cached_data()
    return jsonify(
        last_updated=redis.get('last_updated').decode(),
        statuses=json.loads(redis.get('statuses').decode()),
        data=data,
    )
7

@app.route('/')
def index():
    return render_template(
        'index.html',
        data=get_cached_data(),
        last_updated=redis.get('last_updated').decode()
    )


if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )

import os
import json
import pickle
import logging
from itertools import chain

import arrow
from redis import StrictRedis
from flask import Flask, render_template, jsonify, request

from sources import sources, default

logging.basicConfig(level=logging.DEBUG)

redis = StrictRedis.from_url(os.environ.get("REDIS_URL"))

app = Flask(__name__)
app.json_encoder.default = lambda self, obj: default(obj)
app.json_encoder.indent = 2


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


def get_last_updated():
    return redis.get('last_updated').decode()


def get_status():
    return json.loads(redis.get('statuses').decode())


@app.route('/index.json')
def index_json():
    data = get_cached_data()
    return jsonify(
        last_updated=get_last_updated(),
        statuses=get_status(),
        data=data,
    )


@app.route('/status')
def status():
    return jsonify(get_status())


@app.route('/')
def index():
    return render_template(
        'index.html',
        data=get_cached_data(),
        statuses=get_status(),
        last_updated=get_last_updated()
    )


if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )

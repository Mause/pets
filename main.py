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

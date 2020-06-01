import json
import logging
import os
import pickle
from unittest.mock import Mock

import arrow
from flask import Blueprint, Flask, current_app, jsonify, render_template, request
from redis import StrictRedis

from config import config
from sources import default

logging.basicConfig(level=logging.DEBUG)


app = Blueprint('app', __name__)


def create_app(config=None):
    papp = Flask(__name__)
    papp.register_blueprint(app)
    papp.config.update(config or {})
    papp.redis = (
        Mock(spec=StrictRedis)
        if papp.testing
        else StrictRedis.from_url(config["REDIS_URL"])
    )
    papp.json_encoder.default = lambda self, obj: default(obj)
    papp.json_encoder.indent = 2
    return papp


def get_cached_data():
    data = pickle.loads(current_app.redis.get('data'))
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
    return current_app.redis.get('last_updated').decode()


def get_status():
    return json.loads(current_app.redis.get('statuses').decode())


@app.route('/index.json')
def index_json():
    data = get_cached_data()
    return jsonify(last_updated=get_last_updated(), statuses=get_status(), data=data,)


@app.route('/status')
def status():
    return jsonify(get_status())


@app.route('/')
def index():
    return render_template(
        'index.html',
        data=get_cached_data(),
        statuses=get_status(),
        last_updated=get_last_updated(),
    )


if __name__ == '__main__':
    create_app().run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

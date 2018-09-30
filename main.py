import os
from itertools import chain
from concurrent.futures import ThreadPoolExecutor as PoolExectutor

from tqdm import tqdm
from flask import Flask, render_template, jsonify

from sources import sources

EXECUTOR = PoolExectutor()
app = Flask(__name__)


def get_data():
    data = chain.from_iterable(
        EXECUTOR.map(
            lambda func: list(func()),
            sources,
        )
    )
    data = tqdm(data)
    data = sorted(data, key=lambda item: item.found_on, reverse=True)


@app.route('/index.json')
def index_json():
    return jsonify(get_data())


@app.route('/')
def index():
    return render_template('index.html', data=get_data())


if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )

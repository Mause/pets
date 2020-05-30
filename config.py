import json
import os

try:
    with open('config.json') as fh:
        config = json.load(fh)
except FileNotFoundError:
    config = os.environ

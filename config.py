import os
import json

try:
    with open('config.json') as fh:
        config = json.load(fh)
except FileNotFoundError:
    config = os.environ

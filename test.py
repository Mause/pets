import json
from unittest.mock import patch

import responses

from worker import alert_error

URL = 'https://fake/callback'


@responses.activate
@patch('worker.config', {'XMATTERS_WEBHOOK': URL})
def test_alert_email():
    responses.add(method='POST', url=URL)

    try:
        raise Exception("What the heck?")
    except Exception as e:
        error = e

    alert_error("Busso", error)

    js = json.loads(responses.calls[0].request.body)

    contents = open("tests/data/email.html").read().strip()

    assert js['properties']['message'].strip() == contents

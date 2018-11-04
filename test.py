import responses
from urllib.parse import parse_qsl
from worker import alert_error, MESSAGES_URL


@responses.activate
def test_alert_email():
    responses.add(method="POST", url=MESSAGES_URL)
    responses.add(method='POST', url='https://fake/callback')

    try:
        raise Exception("What the heck?")
    except Exception as e:
        error = e

    alert_error("Busso", error)

    js = dict(parse_qsl(responses.calls[0].request.body))

    assert js["html"].strip() == open("tests/data/email.html").read().strip()

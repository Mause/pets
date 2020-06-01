import json
import pickle

from arrow import Arrow
from betamax import Betamax
from betamax_serializers.yaml11 import YAMLSerializer
from flask import current_app
from pytest import fixture, mark
from requests import Session

from main import create_app
from sources import Pet, sources

Betamax.register_serializer(YAMLSerializer)


with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'


@fixture
def betamax(request):
    session = Session()
    session.headers['Accept-Encoding'] = 'none'  # gzip/deflate breaks with betamax
    with Betamax(session).use_cassette(request.node.name, serialize_with='yaml11'):
        yield session


@mark.parametrize('source', sources)
def test_sources(source, betamax, snapshot):
    snapshot.assert_match(list(source(betamax)))


@fixture
def app():
    return create_app({'TESTING': True})


@fixture
def test_client(app):
    with app.test_client() as tc:
        yield tc


def test_render(test_client, snapshot, app):
    app.redis.get.side_effect = lambda key: {
        'statuses': json.dumps({'swahamish': False}).encode(),
        'data': pickle.dumps(
            [
                Pet(
                    location='Rapture',
                    image=None,
                    breed=None,
                    color=None,
                    gender=None,
                    found_on=Arrow(2020, 1, 1),
                    source='rapture',
                    url='https://rapture.io/lost-and-found',
                )
            ]
        ),
        'last_updated': b'2020-01-01T00:00',
    }[key]

    render = test_client.get('/')

    assert render.status_code == 200

    snapshot.assert_match(render.get_data().decode())

from betamax import Betamax
from betamax_serializers.yaml11 import YAMLSerializer
from pytest import fixture, mark
from requests import Session

from sources import sources

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

import pytest
from server_v2 import PollSession, Run
import psycopg2
from core import read_parameter

from constants import PG_HOST, PG_PASSWORD, PG_USER
PG_DB = 'test2'


@pytest.fixture()
def connector():
    return psycopg2.connect(
        host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASSWORD
    ).cursor()


def test_connection(connector):
    cur = connector.cursor()
    assert cur.execute('SELECT 1') == 0


@pytest.fixture()
def database(dsn):
    pass


@pytest.fixture()
def fake_data():
    pass


def test_session():
    pass
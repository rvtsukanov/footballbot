import pytest
from server_v2 import PollSession, Run
import psycopg2
from pg_snippets import insert_into_session_index, fetch_last_session_session_index, insert_one_player_into_sessions2players
from db.pg.db_creation_scripts import SESSION_INDEX_CREATE_SCRIPT, SESSION2PLAYERS_CREATE_SCRIPT, GAMES_CREATE_SCRIPT

import faker
import random

import datetime
import logging

from constants import PG_HOST, PG_PASSWORD, PG_USER
PG_DB = 'test_data'


@pytest.fixture
def create_session_index(connector):
    cur = connector.cursor()
    cur.execute(SESSION_INDEX_CREATE_SCRIPT)
    try:
        yield connector.commit()
    except:
        cur.execute('''TRUNCATE session_index''')


def insert_into_session_index_fixture(connector, session_start_time, session_expire_time):
    insert_into_session_index(connector, session_start_time=session_start_time,
                              session_expire_time=session_expire_time)


def create_games(connector):
    cur = connector.cursor()
    cur.execute(GAMES_CREATE_SCRIPT)
    connector.commit()


def create_sessions2players(connector):
    cur = connector.cursor()
    cur.execute(SESSION2PLAYERS_CREATE_SCRIPT)
    connector.commit()


@pytest.fixture(scope='function')
def connector():
    logging.info(f'Trying to connect to: {PG_HOST} {PG_DB} {PG_USER} {PG_PASSWORD}')
    connector = psycopg2.connect(
        host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASSWORD
    )
    with connector.cursor() as cur:
        cur.execute('TRUNCATE session_index;')
    yield connector
    with connector.cursor() as cur:
        cur.execute('TRUNCATE session_index;')
        cur.execute('TRUNCATE sessions2players;')
        cur.execute('TRUNCATE games;')

    connector.commit()
    connector.close()


def get_session_id(connector, offset_pair):
    cur = connector.cursor()
    cur.execute('TRUNCATE session_index;')
    now = datetime.datetime.now()
    session_id = insert_into_session_index(connector, session_start_time=(now + datetime.timedelta(days=offset_pair[0])),
                              session_expire_time=(now + datetime.timedelta(days=offset_pair[1])))


    return session_id


@pytest.fixture(scope='session')
def fake():
    return faker.Faker(locale=['ru_RU'])



def fulfill_table_sessions2players(connector, fake, offset_pair):#, get_session_id):
    cur = connector.cursor()

    cur.execute('TRUNCATE sessions2players;')
    connector.commit()

    session_id = get_session_id(connector, offset_pair)

    # cur.execute('select last_value from session_index_session_id_seq;')

    randint = random.randint(0, 10)

    for _ in range(randint):
        insert_one_player_into_sessions2players(connector, session_id=session_id,
                                                now=datetime.datetime.now(), username=fake.user_name(), out=False,
                                                game_date=datetime.date(9999, 12, 12)
                                                )


def test_connection(connector):
    cur = connector.cursor()
    cur.execute('SELECT 1')
    assert cur.fetchall()[0][0] == 1


test_cases = [((-5, 5), True), ((-10, -5), False), ((5, 10), False)]
@pytest.mark.parametrize("offset_pair, expected", test_cases)
def test_session_index(connector, offset_pair, expected, fake):

    fulfill_table_sessions2players(connector, fake, offset_pair)
    run = Run(debug=True)
    logging.info(run.current_poll_session)
    now = datetime.datetime.now()
    index = fetch_last_session_session_index(connector, now=now)
    logging.info(f'Index is {index}')

    assert (run.current_poll_session is not None) == expected


def test_polling():
    run = Run(debug=True)
    run.bot.infinity_polling()


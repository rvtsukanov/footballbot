import pytest
from server_v2 import PollSession, Run
import psycopg2
from core import read_parameter
from pg_snippets import insert_into_session_index, fetch_last_session_session_index, insert_one_player_into_sessions2players
import datetime
import logging

from constants import PG_HOST, PG_PASSWORD, PG_USER
PG_DB = 'test_data'


def create_session_index(connector):
    cur = connector.cursor()
    cur.execute('DROP TABLE IF EXISTS public.session_index')

    # cur.execute('''CREATE SEQUENCE public.session_index_session_id_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647
    # CACHE 1;''')

    creation_sql = '''CREATE TABLE IF NOT EXISTS public.session_index
(
            session_id integer NOT NULL DEFAULT nextval('session_index_session_id_seq'::regclass),
            session_start_time timestamp without time zone,
            session_expire_time timestamp without time zone,
            CONSTRAINT session_index_pkey PRIMARY KEY (session_id)
)
            TABLESPACE pg_default;

            ALTER TABLE public.session_index
                OWNER to admin;
    '''

    cur.execute(creation_sql)
    connector.commit()


def insert_into_session_index_fixture(connector, session_start_time, session_expire_time):
    insert_into_session_index(connector, session_start_time=session_start_time,
                              session_expire_time=session_expire_time)


def create_games(connector):
    cur = connector.cursor()
    cur.execute('DROP TABLE IF EXISTS public.games')
    sql = '''
    CREATE TABLE IF NOT EXISTS public.games
    (
        game_date date NOT NULL,
        cost numeric,
        team_a boolean,
        team_b boolean,
        team_c boolean,
        team_d boolean,
        username "char"[]
    )
    
    TABLESPACE pg_default;
    
    ALTER TABLE public.games
        OWNER to rvtsukanov;
        '''
    cur = connector.cursor()
    cur.execute(sql)
    connector.commit()


def create_sessions2players(connector):
    cur = connector.cursor()
    sql = '''
            CREATE TABLE IF NOT EXISTS public.sessions2players
        (
            game_date date NOT NULL,
            "out" boolean,
            username text COLLATE pg_catalog."default",
            now timestamp without time zone,
            session_id integer
        )
        
        TABLESPACE pg_default;
        
        ALTER TABLE public.sessions2players
            OWNER to rvtsukanov;
    '''

    cur.execute(sql)
    connector.commit()


@pytest.fixture()
def connector():
    return psycopg2.connect(
        host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASSWORD
    )


def test_connection(connector):
    cur = connector.cursor()
    cur.execute('SELECT 1')
    assert cur.fetchall()[0][0] == 1


@pytest.fixture()
def database(dsn):
    pass


@pytest.fixture()
def fake_data(connector):
    connector



test_cases = [((-5, 5),True), ((-10, -5), False), ((5, 10) ,False)]

@pytest.mark.parametrize("offset_pair, expected", test_cases)
def test_session_index(connector, offset_pair, expected):
    create_session_index(connector)
    cur = connector.cursor()
    # cur.execute('SELECT 1 FROM session_index;')

    now = datetime.datetime.now()

    insert_into_session_index(connector, session_start_time=(now + datetime.timedelta(days=-offset_pair[0])),
                              session_expire_time=(now + datetime.timedelta(days=offset_pair[1])))

    run = Run(debug=True)
    logging.info(run.current_poll_session)

    now = datetime.datetime.now()

    index = fetch_last_session_session_index(connector, now=now)

    if index:
        session_id, session_start_time, session_expire_time = index[0]

        insert_one_player_into_sessions2players(connector, session_id=session_id,
                                                now=now, username='rvtsukanov', out=False,
                                                game_date=datetime.date(2022, 11, 11)
                                                )

        insert_one_player_into_sessions2players(connector, session_id=session_id,
                                                now=now, username='gsafyanov', out=False,
                                                game_date=datetime.date(2022, 11, 11)
                                                )

    # assert False

    assert (run.current_poll_session is not None) == expected




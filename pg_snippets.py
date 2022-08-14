import psycopg2
from core import read_parameter
import datetime

import logging
import sys

logger = logging.getLogger("pg_snippet")
logger.setLevel(logging.DEBUG)


handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

TOKEN = read_parameter("token")
SESSION_ADMINS = read_parameter("admins")
GROUP_ID = read_parameter("group_chat_id")

PG_HOST = "localhost"
PG_PASSWORD = read_parameter("pg_password")
PG_DB = read_parameter("pg_db")
PG_USER = read_parameter("pg_user")

MATCHTIME = datetime.time(int(read_parameter("matchtime")), 0, 0, 0)


def insert_into_session_index(connector, **values):
    cursor = connector.cursor()

    session_start_time = values["session_start_time"]
    session_expire_time = values["session_expire_time"]

    logger.info(f"Trying to set: {session_start_time}")
    logger.info(f"Trying to set: {session_expire_time}")

    sql = f"""
        INSERT INTO session_index(
        session_start_time, session_expire_time)
        VALUES ('{session_start_time}', '{session_expire_time}') 
        RETURNING session_id;
    """

    logger.debug(f"By following SQL: {sql}")

    cursor.execute(sql, (session_start_time, session_expire_time))
    # connector.commit()
    return cursor.fetchall()[0][0]


def fetch_last_session_session_index(connector, **values):
    cursor = connector.cursor()
    now = values["now"]

    sql = f"""
         SELECT session_id, session_start_time, session_expire_time FROM session_index 
         WHERE ('{(now)}' BETWEEN session_start_time AND session_expire_time)
         ORDER BY session_id DESC LIMIT 1;
          """

    logger.debug(f"By following SQL: {sql}")
    cursor.execute(
        sql,
    )
    connector.commit()
    return cursor.fetchall()


def fetch_players_by_session_id(connector, **values):
    cursor = connector.cursor()
    session_id = values['session_id']

    sql = f"""
             SELECT DISTINCT username FROM sessions2players WHERE session_id = {int(session_id)} 
           """

    logger.debug(f"By following SQL: {sql}")

    cursor.execute(
        sql,
    )
    connector.commit()
    players_set = cursor.fetchall()
    return [player[0] for player in players_set]


def insert_one_player_into_sessions2players(connector, **values):
    cursor = connector.cursor()

    session_id = values['session_id']
    now = values['now']
    username = values['username']
    out = values['out']
    game_date = values['game_date']

    sql = f"""
            INSERT INTO sessions2players(game_date, out, username, now, session_id)
            VALUES ('{game_date}', '{out}', '{username}', '{now}', '{session_id}');
        """

    logger.debug(f"By following SQL: {sql}")
    print(f"By following SQL: {sql}")

    cursor.execute(
        sql,
    )
    connector.commit()



def create_agg_cumsum_procedures(connector, **values):

    sql = '''
    CREATE FUNCTION int_add_pos_or_zero(int, int)
    RETURNS int
    AS $$
        BEGIN
            RETURN greatest($1 + $2, 0);
        END;
    $$
    LANGUAGE plpgsql
    IMMUTABLE;

    CREATE AGGREGATE add_pos_or_zero(int)(
      SFUNC = int_add_pos_or_zero,
      STYPE = int,
      INITCOND = 0
      );
    '''



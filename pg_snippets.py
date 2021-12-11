import psycopg2
from core import read_parameter
import datetime

import logging

logger = logging.getLogger("pg_snippet")
logger.setLevel(logging.INFO)

import sys

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


connector = psycopg2.connect(
    host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASSWORD
)


def insert_into_session_index(connector, **values):
    cursor = connector.cursor()

    session_start_time = values["session_start_time"]
    session_expire_time = values["session_expire_time"]

    logger.info(f"Trying to set: {session_start_time}")
    logger.info(f"Trying to set: {session_expire_time}")

    sql = f"""
        INSERT INTO session_index(
        session_start_time, session_expire_time)
        VALUES ('{session_start_time}', '{session_expire_time}');
    """

    logger.debug(f"By following SQL: {sql}")

    cursor.execute(sql, (session_start_time, session_expire_time))
    connector.commit()


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
    return cursor.fetchall()


def find_closest_game_date(time, matchday=6):
    return time + datetime.timedelta((matchday - time.weekday()) % 7)


# now = datetime.datetime.now()
# days
# print(now)
# print(now + datetime.timedelta(days=3))


# insert_into_session_index_values = [
#     # First row
#     {
#         "session_start_time": datetime.datetime.now(),
#         "session_expire_time": find_closest_game_date(now),
#     },
#     # Second row
#     {
#         "session_start_time": now,
#         "session_expire_time": now + datetime.timedelta(days=3),
#     },
# ]
#
# for row in insert_into_session_index_values:
#     insert_into_session_index(connector, **row)


values = {"now": datetime.datetime.now()}
result = fetch_last_session_session_index(connector, **values)
print(result)

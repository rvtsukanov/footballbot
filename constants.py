from core import read_parameter
import datetime
import re
import os
import logging


TOKEN = read_parameter("token")
SESSION_ADMINS = read_parameter("admins")
GROUP_ID = read_parameter("group_chat_id")
PG_HOST = read_parameter("DATABASE_URL")
PG_PASSWORD = read_parameter("pg_password")
PG_DB = read_parameter("pg_db")
PG_USER = read_parameter("pg_user")

MATCHTIME = datetime.time(int(read_parameter("matchtime")), 0, 0, 0)
MATCHDAY = 5  # for Sat


# if PG_HOST:
#     _, user, db_token, host, port, db = re.findall(
#         r"(\w+)://(\w+):(\w+)@(.+):(\d+)\/(\w+)", PG_HOST
#     )[0]
# else:
#     user = PG_USER
#     db_token = PG_PASSWORD
#     db = PG_DB
#     host = "localhost"
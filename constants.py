import datetime
import re
import os
import yaml
import logging

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
logging.info(f'Got root dir as {ROOT_DIR}')

CONFIG_PATH = os.path.join(ROOT_DIR, 'config.yaml')
logging.info(f'Config then {CONFIG_PATH}')

NUM_PLAYERS = yaml.safe_load(open(CONFIG_PATH, 'r'))['num_players']
NUM_EXTRA_PLAYERS = yaml.safe_load(open(CONFIG_PATH, 'r'))['num_extra_players']

def read_parameter(param_name):
    if os.getenv(param_name.upper()):
        return os.getenv(param_name.upper())
    elif yaml.safe_load(open(CONFIG_PATH, 'r'))[param_name]:
        return yaml.safe_load(open(CONFIG_PATH, 'r'))[param_name]
    else:
        return ''


TOKEN = read_parameter("token")
SESSION_ADMINS = read_parameter("admins")
GROUP_ID = read_parameter("group_chat_id")
PG_HOST = read_parameter("DATABASE_URL")
PG_PASSWORD = read_parameter("pg_password")
PG_DB = read_parameter("pg_db")
PG_USER = read_parameter("pg_user")

MATCHTIME = datetime.time(int(read_parameter("matchtime")), 0, 0, 0)
MATCHDAY = 5  # for Sat


AVAILABLE_COMMANDS_INLINE_QUERY = {'set_max_players': 'Максимальное число игроков в сессии',
                                   'set_teams_num': 'Число команд в одной игре',
                                   'add_to_current_session': 'Добавить игрока к текущей сессии',
                                   'remove_from_current_session': 'Удалить игрока из текущей сессии'}

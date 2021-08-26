import telebot
import yaml
import logging
import sys
import json
from core import PollSession
import datetime
import psycopg2

TOKEN = yaml.safe_load(open('./config.yaml', 'r'))['token']
SESSION_ADMINS = yaml.safe_load(open('./config.yaml', 'r'))['admins']
GROUP_ID = yaml.safe_load(open('./config.yaml', 'r'))['group_chat_id']

PG_HOST = yaml.safe_load(open('./config.yaml', 'r'))['pg_host']
PG_PASSWORD = yaml.safe_load(open('./config.yaml', 'r'))['pg_password']
PG_DB = yaml.safe_load(open('./config.yaml', 'r'))['pg_db']
PG_USER = yaml.safe_load(open('./config.yaml', 'r'))['pg_user']

log = logging.getLogger('server')
log.setLevel(logging.INFO)

class Run:
    def __init__(self):
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        self.log = logging.getLogger('run_instance')
        self.log.setLevel(logging.INFO)
        self.current_poll_session = None
        self.bot = telebot.TeleBot(TOKEN, parse_mode=None)

        self.conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD)

        self.cursor = self.conn.cursor()
        # self.cursor.execute('SELECT * from sessions123;')
        # print(self.cursor.fetchone())

        @self.bot.message_handler(func=lambda m: m.chat.type == 'group')
        def proceed_group_pluses(message):
            if r.current_poll_session and message.text:
                if '+' in message.text:
                    r.current_poll_session.add_player_to_session(message.from_user.username)
                    # self.cursor.execute("INSERT INTO sesions VALUES ();")
            log.info(f'Have msg: {message}')

        @self.bot.message_handler(commands=['start_new_poll'], func=lambda m: m.from_user.username in SESSION_ADMINS)
        def start_new_poll(message):
            if r.current_poll_session is None or r.current_poll_session.active_time_end >= datetime.datetime.now():
                now = datetime.datetime.now()

                self.log.info('Creating new PollSession ')
                r.current_poll_session = PollSession(active_time_start=datetime.date(2021, 8, 25),
                                                     active_time_end=datetime.date(2021, 8, 27),
                                                     is_closed=False)
                # log.info(r.current_poll_session)
                self.bot.send_message(chat_id=GROUP_ID, text=str(r.current_poll_session))

        @self.bot.message_handler(commands=['check_current_poll'], func=lambda m: m.from_user.username in
                                                                                  SESSION_ADMINS)
        def check_current_poll(message):
            log.info(r.current_poll_session)

    def _estimate_closest_game_date(self, time, matchday='SAT'):


r = Run()
r.bot.polling()
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

MATCHTIME = datetime.time(int(yaml.safe_load(open('./config.yaml', 'r'))['matchtime']), 0, 0, 0)

log = logging.getLogger('server')
log.setLevel(logging.INFO)

class Run:
    def __init__(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        self.log = logging.getLogger('run_instance')
        self.log.setLevel(logging.INFO)
        self.current_poll_session = None
        self.bot = telebot.TeleBot(TOKEN, parse_mode='MARKDOWN')

        self.conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD)

        self.cursor = self.conn.cursor()


        @self.bot.message_handler(commands=['start_new_poll'], func=lambda m: m.from_user.username in SESSION_ADMINS)
        def start_new_poll(message):
            now = datetime.datetime.now()
            self.log.info(message)
            if self.current_poll_session is None or self.current_poll_session.session_end_time <= now:
                # TODO: try to fetch latest session

                matchday = self._find_closest_game_date(now)
                matchtime = datetime.datetime.combine(matchday, MATCHTIME)

                self.current_poll_session = PollSession(session_start_time=now,
                                                     session_end_time=matchtime,
                                                     game_date=matchday,
                                                     is_closed=False)

                self.log.info(f'Creating new PollSession. \n Will active from '
                              f'{r.current_poll_session.session_start_time} to {r.current_poll_session.session_end_time}')

                self.bot.send_message(chat_id=GROUP_ID, text=str(r.current_poll_session))


        @self.bot.message_handler(commands=['check_current_poll'], func=lambda m: m.from_user.username in
                                                                                  SESSION_ADMINS)
        def check_current_poll(message):
            log.info(r.current_poll_session)
            self.bot.send_message(chat_id=GROUP_ID,
                                  text=self.current_poll_session.render_status())


        @self.bot.message_handler(commands=['end_current_poll'], func=lambda m: m.from_user.username in
                                                                                  SESSION_ADMINS)
        def end_current_poll(message):
            if self.current_poll_session:
                log.info(r.current_poll_session)
                self.bot.send_message(chat_id=GROUP_ID, text=str(r.current_poll_session) + "is closed.")



        @self.bot.message_handler(func=lambda m: m.chat.type == 'group')
        def proceed_group_pluses(message):
            if self.current_poll_session and message.text and message.text == '+':

                now = datetime.datetime.now()
                username = message.from_user.username

                self.current_poll_session.add_player_to_session(username)
                print(self.current_poll_session.player_set)
                # if not username in self.current_poll_session.player_set:
                #     print(1111)
                self._add_player_to_db_session(self.current_poll_session, username, out=False, now=now)

            if self.current_poll_session and message.text and message.text == '-':
                now = datetime.datetime.now()
                username = message.from_user.username

                self.current_poll_session.remove_player_from_session(username)
                if username in self.current_poll_session.player_set:
                    self._add_player_to_db_session(self.current_poll_session, username, out=True, now=now)


    def _find_closest_game_date(self, time, matchday=5):
        return (time + datetime.timedelta((matchday - time.weekday()) % 7)).date()


    def _add_player_to_db_session(self, session, username, out, now):

        sql = """INSERT INTO sessions
             VALUES(%s, %s, %s, %s, %s, %s);"""

        self.log.debug(f'executing {sql}')

        self.cursor.execute(sql,
                            (session.game_date,
                            out,
                             session.session_start_time,
                             session.session_end_time,
                             username,
                             now
                             ))

        self.log.debug(f'commiting')
        self.conn.commit()
        self.log.debug(f'committed')



r = Run()
r.bot.polling()
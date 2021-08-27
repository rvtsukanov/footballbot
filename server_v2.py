import telebot
import yaml
import logging
import sys
import json
from core import PollSession, read_parameter
import datetime
import psycopg2
from flask import Flask, request
import re

TOKEN = read_parameter('token')
SESSION_ADMINS = read_parameter('admins')
GROUP_ID = read_parameter('group_chat_id')

PG_HOST = read_parameter('DATABASE_URL')

print('HOST IS: ', PG_HOST)
PG_PASSWORD = read_parameter('pg_password')
PG_DB = read_parameter('pg_db')
PG_USER = read_parameter('pg_user')

MATCHTIME = datetime.time(int(read_parameter('matchtime')), 0, 0, 0)

server = Flask(__name__)

_, user, db_token, host, port, db = re.findall(r'(\w+)://(\w+):(\w+)@(.+):(\d+)\/(\w+)', PG_HOST)[0]

import os

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
            host=host,
            database=db,
            user=user,
            password=db_token)

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
                              f'{self.current_poll_session.session_start_time} to'
                              f' {self.current_poll_session.session_end_time}')

                self.bot.send_message(chat_id=GROUP_ID, text=str(self.current_poll_session))


        @self.bot.message_handler(commands=['check_current_poll'], func=lambda m: m.from_user.username in
                                                                                  SESSION_ADMINS)
        def check_current_poll(message):
            log.info(self.current_poll_session)
            self.bot.send_message(chat_id=GROUP_ID,
                                  text=self.current_poll_session.render_status())


        @self.bot.message_handler(commands=['end_current_poll'], func=lambda m: m.from_user.username in
                                                                                  SESSION_ADMINS)
        def end_current_poll(message):
            if self.current_poll_session:
                log.info(self.current_poll_session)
                self.bot.send_message(chat_id=GROUP_ID, text=str(self.current_poll_session) + "is closed.")



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

        @server.route('/' + TOKEN, methods=['POST'])
        def getMessage():
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            self.bot.process_new_updates([update])
            return "!", 200

        @server.route("/")
        def webhook():
            print('Im in webhook')
            self.bot.remove_webhook()
            self.bot.set_webhook(url='https://doweplayfootball.herokuapp.com/' + TOKEN)
            return "!", 200


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

        self.log.debug(f'writing {username} to db')
        self.conn.commit()
        self.log.debug(f'committed')


if __name__ == "__main__":
    try:
        r = Run()
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)), debug=False)

    except Exception as e:
        print(e)
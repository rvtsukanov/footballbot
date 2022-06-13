import telebot
import logging
import sys
from core import PollSession
import argparse
import datetime
import psycopg2
from flask import Flask
from markups import plus_minus_markup
from scenarios import SESSION_ONLY, GROUP_ONLY, ALWAYS_TRUE
from constants import TOKEN, SESSION_ADMINS, GROUP_ID, PG_HOST, PG_PASSWORD, PG_DB, PG_USER, MATCHTIME, MATCHDAY

from pg_snippets import fetch_last_session_session_index, fetch_players_by_session_id

parser = argparse.ArgumentParser()
parser.add_argument("--debug")

server = Flask(__name__)

log = logging.getLogger("server")
log.setLevel(logging.INFO)


class Run:
    def __init__(self, debug=False):

        self.debug = debug
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        self.log = logging.getLogger("run_instance")
        self.log.setLevel(logging.INFO if not debug else logging.DEBUG)

        self.current_poll_session_message = None

        self.bot = telebot.TeleBot(TOKEN, parse_mode="MARKDOWN")

        if debug:
            self.adjust_launcher_for_infinity_polling()

        self.callback_handlers = {
            self.proceed_group_pluses_from_callback: {"func": ALWAYS_TRUE}
        }

        self.message_handlers = {
            self.start_new_poll: {"func": SESSION_ONLY,
                                  "commands": ["start_new_poll"]},
            self.check_current_poll: {
                "commands": ["check_current_poll"],
                "func": SESSION_ONLY,
            },
            self.end_current_poll: {
                "commands": ["end_current_poll"],
                "func": SESSION_ONLY,
            },
            self.proceed_group_pluses: {"func": GROUP_ONLY},
        }


        self.log.info(f'Trying to connect to: {PG_HOST} {PG_DB} {PG_USER} {PG_PASSWORD}')
        self.conn = psycopg2.connect(
            host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASSWORD
        )

        self.cursor = self.conn.cursor()
        self.current_poll_session = self.get_session()

        self.register_message_handlers(self.message_handlers)
        self.register_callback_handlers(self.callback_handlers)


    def adjust_launcher_for_infinity_polling(self):
        self.bot.remove_webhook()


    def get_session(self):
        self.log.info(f"Attempt to recover existing session ... ")
        index = fetch_last_session_session_index(self.conn, now=datetime.datetime.now())
        self.log.info(f"Got index: {index}")
        if index:
            session_id, session_start_time, session_expire_time = index[0]
            players = fetch_players_by_session_id(
                connector=self.conn, session_id=session_id
            )
            self.log.info(f"Players are: {players}")

            pollsession = PollSession(
                session_start_time=session_start_time,
                session_end_time=session_expire_time,
                game_date=session_start_time,
                is_closed=False,
            )
            return pollsession


    def register_message_handlers(self, handlers):
        for handler, kwargs in handlers.items():
            self.bot.add_message_handler(
                self.bot._build_handler_dict(handler, **kwargs)
            )

    def register_callback_handlers(self, handlers):
        for handler, kwargs in handlers.items():
            self.bot.add_callback_query_handler(
                self.bot._build_handler_dict(handler, **kwargs)
            )

    def start_new_poll(self, message):
        now = datetime.datetime.now()
        self.log.info(message)
        if (
            self.current_poll_session is not None
        ):
            self.log.warning(f'Overwriting existing poll-session')

        matchday = self._find_closest_game_date(now)
        matchtime = datetime.datetime.combine(matchday, MATCHTIME)

        self.current_poll_session = PollSession(
            session_start_time=now,
            session_end_time=matchtime,
            game_date=matchday,
            is_closed=False,
        )

        self.log.info(
            f"Creating new PollSession. \n Will active from "
            f"{self.current_poll_session.session_start_time} to"
            f" {self.current_poll_session.session_end_time}"
        )

        msg = self.bot.send_message(
            chat_id=GROUP_ID,
            text=self.current_poll_session.render_status(),
            reply_markup=plus_minus_markup(),
        )

        self.log.debug(f"Saving current message id: {msg.message_id}")
        self.current_message_id = msg.message_id

        self.bot.pin_chat_message(
            chat_id=GROUP_ID, message_id=self.current_message_id
        )

    def check_current_poll(self, message):
        log.info(self.current_poll_session)
        self.bot.send_message(
            chat_id=GROUP_ID, text=self.current_poll_session.render_status()
        )

    def end_current_poll(self, message):
        if self.current_poll_session:
            log.info(self.current_poll_session)
            self.bot.send_message(
                chat_id=GROUP_ID, text=str(self.current_poll_session) + "is closed."
            )

    def proceed_group_pluses_from_callback(self, query):

        now = datetime.datetime.now()

        if self.current_poll_session and query.data and query.data == "+":

            username = query.from_user.username

            self.current_poll_session.add_player_to_session(username)
            self._add_player_to_db_session(
                self.current_poll_session, username, out=False, now=now
            )
            self.bot.edit_message_text(
                text=self.current_poll_session.render_status(),
                chat_id=GROUP_ID,
                message_id=self.current_message_id,
                reply_markup=plus_minus_markup(),
            )

        if self.current_poll_session and query.data and query.data == "-":

            username = query.from_user.username

            self.current_poll_session.remove_player_from_session(username)

            self._add_player_to_db_session(
                self.current_poll_session, username, out=True, now=now
            )
            self.bot.edit_message_text(
                text=self.current_poll_session.render_status(),
                chat_id=GROUP_ID,
                message_id=self.current_message_id,
                reply_markup=plus_minus_markup(),
            )

    def proceed_group_pluses(self, message):
        if self.current_poll_session and message.text and message.text == "+":

            now = datetime.datetime.now()
            username = message.from_user.username

            self.current_poll_session.add_player_to_session(username)
            self._add_player_to_db_session(
                self.current_poll_session, username, out=False, now=now
            )

        if self.current_poll_session and message.text and message.text == "-":
            now = datetime.datetime.now()
            username = message.from_user.username

            self.current_poll_session.remove_player_from_session(username)
            if username in self.current_poll_session.player_set:
                self._add_player_to_db_session(
                    self.current_poll_session, username, out=True, now=now
                )
        #
        # @server.route('/' + TOKEN, methods=['POST'])
        # def getMessage():
        #     json_string = request.get_data().decode('utf-8')
        #     update = telebot.types.Update.de_json(json_string)
        #     self.bot.process_new_updates([update])
        #     return "!", 200
        #
        # @server.route("/")
        # def webhook():
        #     print('Im in webhook')
        #     self.bot.remove_webhook()
        #     self.bot.set_webhook(url='https://doweplayfootball.herokuapp.com/' + TOKEN)
        #     return "!", 200

    def _find_closest_game_date(self, time, matchday=MATCHDAY):
        return (time + datetime.timedelta((matchday - time.weekday()) % 7)).date()

    def _add_player_to_db_session(self, session, username, out, now):

        sql = """INSERT INTO sessions
             VALUES(%s, %s, %s, %s, %s, %s);"""

        self.log.debug(f"executing {sql}")

        self.cursor.execute(
            sql,
            (
                session.game_date,
                out,
                session.session_start_time,
                session.session_end_time,
                username,
                now,
            ),
        )

        self.log.debug(f"writing {username} to db")
        self.conn.commit()
        self.log.debug(f"committed")


if __name__ == "__main__":
    # try:
    args = parser.parse_args()
    # r = Run(debug=args.debug)
    r = Run(debug=True)
    # r.bot.remove_webhook()
    r.bot.infinity_polling()
    # server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)), debug=False)

    # except Exception as e:
    #     print(e)

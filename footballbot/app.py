import os

from footballbot import create_app

from footballbot.extensions import db, create_bot
# from footballbot.telegrambot import handlers
from footballbot.extensions import start_bot_infinity_polling

from tests.scenarios import make_scenario_for_UAT

from config import Config
import telebot
import logging

import threading

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
# log = logging.getLogger("root_app")


app = create_app()
bot = create_bot(app.config)


config = app.config

print(f'HERE AS WELL, {config}')

# IDK if really needed
if __name__ == "__main__":
    app.run(ssl_context=(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV), use_reloader=False)


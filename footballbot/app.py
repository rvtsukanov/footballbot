import os

from footballbot import create_app
from footballbot import app


from footballbot.extensions import db
from footballbot.extensions import start_bot_infinity_polling
from tests.scenarios import make_scenario_for_UAT

import logging

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

config = app.config

if config['RUN_TELEGRAM_BOT']:
    from footballbot.telegrambot import handlers
    from footballbot.telegrambot import handlers_createpollsession


# IDK if really needed
if __name__ == "__main__":
    app.run(ssl_context=(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV), use_reloader=False)

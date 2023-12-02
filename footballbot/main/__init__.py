from flask import Blueprint
bp = Blueprint('main', __name__)
tg = Blueprint('telegram', __name__, url_prefix='/tg')

# TODO: find out WTF?
# sqlalch. is not creating tables without direct importing
from footballbot.main import routes

from config import BaseConfig

config = BaseConfig()

if config.RUN_TELEGRAM_BOT:
    from footballbot.main import routes_telegram


from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth
from config import BaseConfig, TestConfig, ProductionConfig
import telebot
import time
import logging
import os
from distutils.util import strtobool

import threading
from telebot.async_telebot import AsyncTeleBot
from telebot import custom_filters

logger = logging.getLogger('bot_init')

config_class = BaseConfig if os.getenv('FLASK_DEBUG', default=False) else ProductionConfig
config = config_class()

from telebot.storage import StateMemoryStorage

def create_bot(nonexisting=False):
    if not nonexisting:
        state_storage = StateMemoryStorage()
        print('Creating bot')
        print(f'CFG (IS DEBUG): {config.DEBUG} {not config.DEBUG}')
        bot = telebot.TeleBot(config.API_TOKEN, threaded=False, num_threads=1, parse_mode='html',
                              state_storage=state_storage)

        bot.add_custom_filter(custom_filters.StateFilter(bot))
        bot.add_custom_filter(custom_filters.IsDigitFilter())

        # if strtobool(os.getenv('FLASK_PRODUCTION_SERVER', default=False)) == True:
        if os.getenv('FLASK_PRODUCTION_SERVER', default=False) == True:
            logger.info('Removing old webhook')
            bot.remove_webhook()
            logger.info('Sleep 10 seconds')
            time.sleep(1)
            logger.info(f'Setting new url: {config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH}')
            print(f'Setting new url: {config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH}')
            bot.set_webhook(url=config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH,
                            certificate=open(config.WEBHOOK_SSL_CERT, 'r'))
        else:
            logger.info('Running local-threaded version of polling')
            bot.remove_webhook()
            time.sleep(1)
            logging.info('Starting new thread for polling')
            print('Starting new thread for polling')
            threading.Thread(target=start_bot_infinity_polling, args=(bot, )).start()
            logging.info('Starting Flask')
        return bot
    else:
        return None


def start_bot_infinity_polling(bot):
    logger.info('Start infinity polling')
    print('Start infinity polling!')
    bot.infinity_polling(timeout=4)


auth = HTTPTokenAuth()
db = SQLAlchemy()

if config.RUN_TELEGRAM_BOT:
    print('Creating bot!')
    bot = create_bot() #TODO: uncomment

fsa = {}  # very dumb way to realise it but anyway...


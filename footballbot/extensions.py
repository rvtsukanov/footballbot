from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth
from config import Config, ProductionConfig
import telebot
import time
import logging
import os

import threading
from telebot.async_telebot import AsyncTeleBot

logger = logging.getLogger('bot_init')

def create_bot():
    config_class = Config if os.getenv('FLASK_DEBUG', default=False) else ProductionConfig
    config = config_class()
    print('Creating bot')
    print(f'CFG: {config.DEBUG}')
    bot = telebot.TeleBot(config.API_TOKEN, threaded=False, num_threads=1, parse_mode='html')

    if not config.DEBUG:
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


def start_bot_infinity_polling(bot):
    logger.info('Start infinity polling')
    bot.infinity_polling(timeout=4)


auth = HTTPTokenAuth()
db = SQLAlchemy()
# bot = create_bot()
fsa = {}  # very dumb way to realise it but anyway...


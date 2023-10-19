from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth
from config import Config
import telebot
import time
import logging

# def create_bot(config):
#     config = Config()
#     bot = telegrambot.TeleBot(config.API_TOKEN)
#     bot.remove_webhook()
#     time.sleep(0.1)
#     bot.set_webhook(url=config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH,
#                     certificate=open(config.WEBHOOK_SSL_CERT, 'r'))
#
#     return bot

def create_bot(config):
    bot = telebot.TeleBot(config.API_TOKEN)

    if config.WEBHOOK_HOST == '127.0.0.1':
        print('Start polling')
        # bot.infinity_polling()

    else:
        print('Removing old webhook')
        bot.remove_webhook()
        print('Sleep 10 seconds')
        time.sleep(10)
        print(f'Setting new url: {config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH}')
        bot.set_webhook(url=config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH,
                        certificate=open(config.WEBHOOK_SSL_CERT, 'r'))

    return bot


config = Config()
auth = HTTPTokenAuth()
db = SQLAlchemy()
bot = create_bot(config)

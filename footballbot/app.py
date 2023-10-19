from footballbot import create_app
from footballbot.extensions import create_bot

from config import Config
import telebot
import logging
app = create_app()

config = Config()
print('Creating bot!')
bot = create_bot(config)

# IDK if really needed
if __name__ == "__main__":
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    app.run(ssl_context=(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV))

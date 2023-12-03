import os
import datetime
basedir = os.path.abspath(os.path.dirname(__file__))

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic import SecretStr, AnyUrl

class BaseConfig(BaseSettings):
    SECRET_KEY: str = os.environ.get('SECRET_KEY', default='1' * 32)
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(basedir, 'database.db')  # TODO: not overriding via test conf
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    MATCHTIME: datetime.time = datetime.time(11, 0)
    MATCHDAY: int = 5  # for Sat
    WEBHOOK_SSL_CERT: str = f'{basedir}/footballbot/webhook_cert.pem'  # Path to the ssl certificate
    WEBHOOK_SSL_PRIV: str = f'{basedir}/footballbot/webhook_pkey.pem'  # Path to the ssl private key
    WEBHOOK_HOST: str = os.environ.get('PUBLIC_IP', default='127.0.0.1')
    WEBHOOK_PORT: int = 443  # 443, 80, 88 or 8443 (port need to be 'open')
    # WEBHOOK_PORT = 5000  # 443, 80, 88 or 8443 (port need to be 'open')
    WEBHOOK_LISTEN: str = '0.0.0.0'  # In some VPS you may need to put here the IP addr
    API_TOKEN: str = '1462545698:AAEkNSWI7BRhugCWmvneBYrMeQRgaPAfIr0'
    WEBHOOK_URL_BASE: str = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
    WEBHOOK_URL_PATH: str = "/%s/" % (API_TOKEN)
    GROUP_ID: int = -539481325
    DEBUG: bool = True
    # SERVER_NAME = '127.0.0.1'
    PREFERRED_URL_SCHEME: str = 'https'
    RUN_TELEGRAM_BOT: bool = True
    GAME_COST: int = 650


class TestConfig(BaseConfig):
    RUN_TELEGRAM_BOT: bool = False
    # SQLALCHEMY_DATABASE_URI: str = 'sqlite://'
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///' + os.path.join(basedir, 'testslocal.db')


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:////var/lib/database2/database.db'
    WEBHOOK_HOST: str = os.environ.get('PUBLIC_IP', default='127.0.0.1')
    API_TOKEN: str = '1462545698:AAEkNSWI7BRhugCWmvneBYrMeQRgaPAfIr0'  # if you want another bot?
    GROUP_ID: int = -539481325  # testing env
    DEBUG: bool = False
    TESTING: bool = False
    FLASK_ENV: str = 'production'
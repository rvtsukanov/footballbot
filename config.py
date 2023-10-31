import os
import datetime
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', default='1' * 32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(basedir, 'database.db')  # TODO: not overriding via test conf
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MATCHTIME = datetime.time(11, 0)
    MATCHDAY = 5  # for Sat
    WEBHOOK_SSL_CERT = f'{basedir}/footballbot/webhook_cert.pem'  # Path to the ssl certificate
    WEBHOOK_SSL_PRIV = f'{basedir}/footballbot/webhook_pkey.pem'  # Path to the ssl private key
    WEBHOOK_HOST = os.environ.get('PUBLIC_IP', default='127.0.0.1')
    WEBHOOK_PORT = 443  # 443, 80, 88 or 8443 (port need to be 'open')
    # WEBHOOK_PORT = 5000  # 443, 80, 88 or 8443 (port need to be 'open')
    WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
    API_TOKEN = ''
    WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
    WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)
    GROUP_ID = -539481325
    DEBUG = True
    # SERVER_NAME = '127.0.0.1'
    PREFERRED_URL_SCHEME = 'https'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////var/lib/database2/database.db'
    WEBHOOK_HOST = os.environ.get('PUBLIC_IP', default='127.0.0.1')
    API_TOKEN = ''  # if you want another bot?
    GROUP_ID = -539481325  # testing env
    DEBUG = False
    TESTING = False
    FLASK_ENV = 'production'
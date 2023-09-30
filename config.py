import os
import datetime
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(basedir, 'database.db')  # TODO: not overriding via test conf
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MATCHTIME = datetime.time(11, 0)
    MATCHDAY = 5  # for Sat
    # FLASK_APP='app.py'
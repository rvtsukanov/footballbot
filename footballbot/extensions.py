from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth()
db = SQLAlchemy()

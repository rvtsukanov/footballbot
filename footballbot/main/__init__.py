from flask import Blueprint
bp = Blueprint('main', __name__)

# TODO: find out WTF?
from footballbot.main import routes
from flask import Blueprint
bp = Blueprint('main', __name__)

# TODO: find out WTF?
# sqlalch. is not creating tables without direct importing
from footballbot.main import routes
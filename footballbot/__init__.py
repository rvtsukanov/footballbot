from flask import Flask
from config import Config, ProductionConfig
from footballbot.extensions import db, auth, create_bot
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from footballbot.models.transactions import Transaction
from footballbot.models.pollsession import Pollsession
from footballbot.models.pollsession2player import Pollsession2Player
from footballbot.models.player import Player
import os
import telebot
import time

class CustomView(ModelView):
    def is_accessible(self):
        return auth

    column_display_pk = True
    column_hide_backrefs = False
    # column_list = ('pollsession_id', 'player_id', 'insert_dt')

class CustomViewP2P(ModelView):
    # def is_accessible(self):
    #     return login.current_user.is_authenticated

    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('pollsession_id', 'player_id', 'insert_dt')

def create_app(config_class=ProductionConfig):
    config_class = Config if os.getenv('FLASK_DEBUG', default=False) else ProductionConfig
    app = Flask(__name__)

    app.config.from_object(config_class)
    db.init_app(app)

    # app.config['FLASK_ADMIN_SWATCH'] = 'superhero'
    app.config['FLASK_ADMIN_SWATCH'] = 'Superhero'
    admin = Admin(app, name='', template_mode='bootstrap3')

    admin.add_view(ModelView(Transaction, db.session))
    admin.add_view(CustomView(Pollsession, db.session))
    admin.add_view(CustomViewP2P(Pollsession2Player, db.session))
    admin.add_view(CustomView(Player, db.session))

    from footballbot.main import bp as main_bp
    app.register_blueprint(main_bp)


    return app

# bot = create_bot(app.config) # its wrong place for bot

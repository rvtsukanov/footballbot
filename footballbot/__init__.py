from flask import Flask
from config import Config
from footballbot.extensions import db
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from footballbot.models.transactions import Transaction
from footballbot.models.pollsession import Pollsession
from footballbot.models.pollsession2player import Pollsession2Player
from footballbot.models.player import Player

class CustomView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('pollsession_id', 'player_id', 'insert_dt')

class CustomViewP2P(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('pollsession_id', 'player_id', 'insert_dt')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # app.config['FLASK_ADMIN_SWATCH'] = 'superhero'
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='', template_mode='bootstrap3')

    admin.add_view(ModelView(Transaction, db.session))
    admin.add_view(CustomView(Pollsession, db.session))
    admin.add_view(CustomViewP2P(Pollsession2Player, db.session))
    admin.add_view(CustomView(Player, db.session))

    from footballbot.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
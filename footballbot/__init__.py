from flask import Flask
from config import Config
from footballbot.extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    from footballbot.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
from footballbot.extensions import db
from footballbot.models.player import Player
from footballbot import app

def admin_only(func):
    def wrapper(*args, **kwargs):
        message = args[0]
        with app.app_context():
            player = Player.find_player(player_id=message.from_user.id)
            role = player.get_role()
            if role == 'admin':
                func(*args, **kwargs)
    return wrapper
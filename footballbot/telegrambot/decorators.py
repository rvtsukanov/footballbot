from footballbot.extensions import db
from footballbot.models.player import Player
from footballbot import app

def admin_only(func):
    print(func)
    def wrapper(*args, **kwargs):
        message = args[0]
        print('AA!', args, kwargs)
        print('MSG!', message)

        with app.app_context():
            player = Player.find_player(player_id=message.chat.id)
            role = player.get_role()
            print(f'Role: {role}')
            print(f'TG: {player.telegram_name}')

            if player.telegram_name == 'rvtsukanov':
                val = func(*args, **kwargs)

        # return val

    return wrapper
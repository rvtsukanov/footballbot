from footballbot.extensions import db

class Player(db.Model):
    player_id = db.Column(db.Integer, primary_key=True, nullable=False)
    telegram_name = db.Column(db.String)

    @classmethod
    def find_player(cls, player_id=None, telegram_name=None):
        if telegram_name:
            return cls.query.filter_by(telegram_name=telegram_name).one()

        if player_id:
            return cls.query.filter_by(player_id=player_id).one()


    def __repr__(self):
        return f'{self.telegram_name}'

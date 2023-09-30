from footballbot.extensions import db
import datetime
from sqlalchemy_serializer import SerializerMixin


class Pollsession2Player(db.Model, SerializerMixin):
    row_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)

    pollsession_id = db.Column(db.Integer, db.ForeignKey('pollsession.pollsession_id'))

    insert_dt = db.Column('insert_dt', db.DateTime, default=datetime.datetime.utcnow)

    player = db.relationship('Player')
    player_id = db.Column(db.Integer, db.ForeignKey('player.player_id'))

    def __le__(self, other):
        return self.insert_dt <= other.insert_dt

    def __lt__(self, other):
        return self.insert_dt <= other.insert_dt
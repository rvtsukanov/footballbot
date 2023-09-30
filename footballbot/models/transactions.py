from footballbot.extensions import db
from sqlalchemy_serializer import SerializerMixin
import datetime


class Transaction(db.Model, SerializerMixin):
    serialize_only = ('player', 'transaction_dt', 'amount', 'description')

    transaction_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    transaction_dt = db.Column('transaction_dt', db.DateTime, default=datetime.datetime.utcnow)

    player = db.relationship('Player')
    player_id = db.Column(db.Integer, db.ForeignKey('player.player_id'))

    amount = db.Column(db.Double)
    description = db.Column(db.String)

    def add_transaction(self):
        db.session.add(self)
        db.session.commit()
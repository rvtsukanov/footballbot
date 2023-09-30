from footballbot.extensions import db
from footballbot.models.common import SerializerAlchemyMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import desc, asc, func
from functools import reduce

class Player(db.Model, SerializerMixin):

    # serialize_only
    serialize_rules = ('-pollsession', '-transactions', '-secret')

    player_id = db.Column(db.Integer, primary_key=True, nullable=False)
    telegram_name = db.Column(db.String)

    role = db.Column(db.String, default='player', nullable=False)
    secret = db.Column(db.String)

    transactions = db.relationship('Transaction', lazy='dynamic', viewonly=True)

    @classmethod
    def find_player(cls, player_id=None, telegram_name=None):
        if telegram_name:
            return cls.query.filter_by(telegram_name=telegram_name).first()

        if player_id:
            return cls.query.filter_by(player_id=player_id).first()


    @classmethod
    def verify_token(cls, secret):
        return cls.query.filter_by(secret=secret).first()


    def get_role(self):
        return self.role

    def get_last_n_transactions(self, n: int):
        return self.transactions.order_by(desc('transaction_dt')).limit(n).all()


    def sum_up_all_transactions(self):
        if self.transactions.all():
        # TODO: rewrite with SQL
            return reduce(lambda x, y: x + y, [t.amount for t in self.transactions])
        else:
            return 0


    def __repr__(self):
        return f'{self.telegram_name}'

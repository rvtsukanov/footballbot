import logging
import math

from footballbot.extensions import db
from sqlalchemy_serializer import SerializerMixin
from footballbot.models.pollsession2player import Pollsession2Player
from footballbot.models.transactions import Transaction
from footballbot.helpers import find_closest_game_date
import datetime
from sqlalchemy import and_
import json
from collections import Counter
from sqlalchemy.exc import NoResultFound

_find_closest_game_date = lambda context: find_closest_game_date(context.get_current_parameters()['creation_dt'])

class Pollsession(db.Model, SerializerMixin):

    pollsession_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    teams_number = db.Column(db.Integer)
    max_players_per_team = db.Column(db.Integer)
    pinned_message_id = db.Column(db.Integer)
    player_votes = db.relationship('Pollsession2Player', lazy='dynamic',
                                   cascade="all, delete")

    creation_dt = db.Column('creation_dt', db.DateTime, default=datetime.datetime.now)
    matchtime_dt = db.Column('matchtime_dt', db.DateTime, default=_find_closest_game_date)

    is_calculated = db.Column('is_calculated', db.Boolean, default=False)

    @classmethod
    def check_if_active_exists(cls):
        now = datetime.datetime.now()
        if cls.query.filter(and_(now >= cls.creation_dt, now <= cls.matchtime_dt)).all():
            return True
        else:
            return False

    def check_if_active(self):
        now = datetime.datetime.now()
        return now >= self.creation_dt and now <= self.matchtime_dt

    @property
    def is_active(self):
        return self.check_if_active()

    @property
    def player_votes_rendered(self):
        return self.player_votes.all()

    @property
    def max_players(self):
        return self.teams_number * self.max_players_per_team

    @property
    def current_players_num(self):
        return len(self.player_votes.all())

    def _check_new_players_available(self):
        return self.max_players > self.current_players_num

    def __repr__(self):
        return f'POLL<{self.pollsession_id}][{self.get_players_telegram_names()}>'

    @classmethod
    def fetch_last_pollsession(cls):
        return db.session.query(cls).order_by(cls.pollsession_id.desc()).first()

    @classmethod
    def fetch_active_pollsession(cls):
        now = datetime.datetime.now()
        try:
            ans = cls.query.filter(and_(now >= cls.creation_dt, now <= cls.matchtime_dt)).one()
            logging.info(f'found: {ans}')
            return ans

        except NoResultFound:
            return []


    def get_lastly_added_player(self):
        return self.player_votes.order_by(Pollsession2Player.insert_dt.desc()).first().player

    def get_lastly_added_n_players(self, n):
        return [vote.player for vote in self.player_votes.order_by(Pollsession2Player.insert_dt.desc()).limit(n).all()]

    def decrease_num_players_by_n(self, n):
        last_added_players = self.get_lastly_added_n_players(n)
        if self.current_players_num >= len(last_added_players):
            for player in last_added_players:
                self.delete_player(player)

            self.max_players_per_team -= math.floor(n // self.teams_number)

        db.session.add(self)
        db.session.commit()


    def increase_num_players_by_n(self, n):
        self.max_players_per_team += math.floor(n // self.teams_number)
        db.session.add(self)
        db.session.commit()


    def add_player(self, player):
        if self._check_new_players_available():
            self.player_votes.append(Pollsession2Player(player=player))
            db.session.add(self)
            db.session.commit()
        else:
            raise ValueError(f'Max amount of players ({self.max_players}) reached')


    def delete_player(self, player):
        vote = self.player_votes.order_by('insert_dt').filter(Pollsession2Player.player == player).first()
        if vote:
            db.session.delete(vote)
            db.session.commit()
        else:
            raise ValueError(f'Player {player} is not presented in {self}')

    def get_players_telegram_names(self):
        votes = self.player_votes.all()
        if votes:
            return [vote.player.telegram_name for vote in votes]
        else:
            return []


    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def calculate_pollsession(self, amount,
                              exceptions=None):
        n = len(self.player_votes_rendered)
        if n > 0:
            if not self.is_active or not self.is_calculated:
                transactions = []
                for vote in self.player_votes_rendered:
                    transactions.append(Transaction(player=vote.player, amount=-amount,
                                description=f'Игра {self.matchtime_dt.date()}'))
                self.is_calculated = True
                db.session.add_all(transactions)
                db.session.commit()
            else:
                raise ValueError('Session is active or already calculated.')
        else:
            raise ValueError('Vote list is emtpy.')

    @classmethod
    def find_pollsession_by_id(cls, pollsession_id):
        return cls.query.filter_by(pollsession_id=pollsession_id).first()

    @classmethod
    def find_pollsession_by_message(cls, message_id):
        return cls.query.filter_by(pinned_message_id=message_id).one()

    @classmethod
    def find_all_uncalculated_sessions(cls):
        return cls.query.filter_by(is_calculated=False).all()

    def render(self):
        MONEY = '💰'
        DONE = '✅'
        emoji_status = u'\U000027a1' if self._check_new_players_available() else u'\U0000274c'

        if self.is_calculated:
            emoji_status = MONEY + DONE

        header = emoji_status + f'<b> Голосование от {self.creation_dt.date()} \nдля записи на игру: {self.matchtime_dt.date()}</b> \n'
        BARS_NUM = 10
        FILLED_RECT = '□'
        EMPTY_RECT = '■'
        BULLET = '▶'
        progress_bar = [FILLED_RECT] * BARS_NUM
        for i in range(int(BARS_NUM * self.current_players_num / self.max_players)):
            progress_bar[i] = EMPTY_RECT
        status_bar = f'<b> {"".join(progress_bar)}  [{self.current_players_num} | {self.max_players}]</b>'
        spaces = '\n'
        rows = [header, status_bar, spaces]
        telegram_names = self.get_players_telegram_names()
        counts = Counter(telegram_names)
        for nick, num in counts.items():
            if num == 1:
                row = f'{BULLET} @{nick}'
            elif num > 1:
                row = f'{BULLET} @{nick} (x{num})'
            rows.append(row)
        return '\n'.join(rows) + '\n'

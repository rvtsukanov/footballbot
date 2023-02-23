from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, Time, Sequence, Date, Float

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
# from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import desc
import datetime
from sqlalchemy import and_
from sqlalchemy.orm import joinedload

import logging

from sqlalchemy.orm.exc import NoResultFound

from constants import PG_USER, PG_PASSWORD, PG_HOST

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# # create the extension
# db = SQLAlchemy()
# # create the app
# app = Flask(__name__)
# # configure the SQLite database, relative to the app instance folder
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# # initialize the app with the extension
# db.init_app(app)


Base = declarative_base()
metadata = MetaData()


class Session2Player(Base):
    __tablename__ = "sessions2players_orm"

    row_id = Column(Integer, autoincrement=True, primary_key=True)  # do not like but ...

    game_id = Column(Integer, ForeignKey('game_index_orm.game_id'))
    # session = relationship('PollSessionIndex')
    session_id = Column(Integer, ForeignKey('session_index_orm_wide.session_id'))
    user = relationship('User')
    user_id = Column(Integer, ForeignKey('users.user_id'))
    insert_time = Column(DateTime)

    def __repr__(self):
        return f'Pollsession_association({self.session_id}:{self.username})'


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    telegram_id = Column(Integer, )
    username = Column(String)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.user_id}::@{self.username})'
    # relationship()

    def get_all_transactions(self, session):
        return session.query(Transactions).filter(Transactions.user_id == self.user_id).order_by(Transactions.transaction_time).all()


    def get_last_transactions(self, session, n):
        return session.query(Transactions).filter(Transactions.user_id == self.user_id).order_by(
            Transactions.transaction_time).limit(n).all()


    def get_balance(self, session):
        transactions = self.get_all_transactions(session)
        return sum(transactions)


class Transactions(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship('User')

    transaction_time = Column(DateTime, default=datetime.datetime.utcnow)

    description = Column(String)
    amount = Column(Integer)

    def __repr__(self):
        return f'TRZ({self.user_id}->{self.amount})'


    def __add__(self, other):
        if isinstance(other, Transactions):
            return self.amount + other.amount
        elif isinstance(other, int):
            return self.amount + other


    def __radd__(self, other):
        return self.__add__(other)


class PollSessionIndex(Base):

    __tablename__ = "session_index_orm_wide"
    session_id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)

    session_start_time = Column(DateTime)
    session_end_time = Column(DateTime)

    game_id = Column(Integer)
    game = relationship('GameIndex')

    teams_number = Column(Integer)
    max_players_per_team = Column(Integer)
    pinned_message_id = Column(Integer)

    # users = relationship(
    #     'Session2Player', backref='user', order_by='Session2Player.insert_time',
    #     lazy='joined'
    # )

    # users = relationship('User', secondary='sessions2players_orm', back_populates='session_index_orm_wide')
    users = relationship('User', secondary='sessions2players_orm')

    def __repr__(self):
        return f'Pollsession({self.session_id}:)'


    @classmethod
    def fetch_active_session(cls, session, now):
        try:
            result = session.query(cls).filter((cls.session_start_time <= now) & (cls.session_end_time >= now)).first()
            return result
        except Exception as e:
            print(e)
            pass


    @classmethod
    def fetch_last_active_session_id(cls, session, now):
        try:
            result = session.query(cls).filter((cls.session_start_time <= now) & (cls.session_end_time >= now)).first()
            return result if result else 0
        except NoResultFound:
            logging.info(f'Got no active session')
            return 0


    def add_player(self, session, user):
        if len(self.users) < self.max_players_per_team:
            self.users.append(user)
        else:
            logging.warning(f'Num players {self.max_players_per_team} of current session is exceeded.')
        session.commit()


    @classmethod
    def get_current_list_of_players(cls, session):
        now = datetime.datetime.now()
        active_session = PollSessionIndex.fetch_active_session(session, now=now)

        # return active_session.username
        return [item.username for item in active_session.users]


    def remove_player(self, session, user):
        '''
        Weird but cant invent better :c

        :param session:
        :param username:
        :return:
        '''
        if user in self.users:
            self.users.remove(user)

        else:
            logging.error(f'{user} is not in current session.')



    @classmethod
    def fetch_exact_pollsession(cls, session, pollsession_id):
        return session.query(cls).filter(cls.session_id == pollsession_id).options(joinedload(cls.users)).one()


    # @classmethod
    # def remove_player(cls, session, username):
    #     cls.dele


    @classmethod
    def fetch_all_users_by_session_id(cls, session, session_id: int):
        try:
            one_session = session.query(cls).filter(cls.session_id == session_id).options(joinedload(cls.users)).one()
            return [item.username for item in one_session.users]
        except NoResultFound:
            logging.info(f'Got empty user set: {cls} - {session_id}')
            return []


    def _modify_session(self, session, attribute, new_value):
        setattr(self, attribute, new_value)
        session.commit()


    # @classmethod
    # def add_player(cls):
    #     pass


    # @classmethod
    # def remove_player(cls):
    #     pass


class GameIndex(Base):

    __tablename__ = "game_index_orm"
    game_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(ForeignKey("session_index_orm_wide.session_id"))

    session = relationship('PollSessionIndex')
    session2player = relationship('Session2Player')



engine = create_engine(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/test_data", echo=True)



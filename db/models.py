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

Base = declarative_base()
metadata = MetaData()


class Session2Player(Base):
    __tablename__ = "sessions2players_orm"

    row_id = Column(Integer, autoincrement=True, primary_key=True)  # do not like but ...

    game_id = Column(Integer, ForeignKey('game_index_orm.game_id'))
    session = relationship('PollSessionIndex')
    session_id = Column(Integer, ForeignKey('session_index_orm_wide.session_id'))
    username = Column(String)
    insert_time = Column(DateTime, )

    def __repr__(self):
        return f'{self.__class__.__name__}({self.session_id}:{self.username})'


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

    username = relationship(
        'Session2Player', backref='user', order_by='Session2Player.insert_time',
        lazy='joined'
    )

    def __repr__(self):
        return f'{self.__class__.__name__}({self.session_id}:{self.username})'


    @classmethod
    def fetch_active_session(cls, session, now):
        try:
            result = session.query(cls).filter((cls.session_start_time <= now) & (cls.session_end_time >= now)).first()
            print(f'RES: {result}')
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


    def add_player(self, session, username):
        self.username.append(Session2Player(username=username, insert_time=datetime.datetime.now()))
        session.commit()


    @classmethod
    def get_current_list_of_players(cls, session):
        now = datetime.datetime.now()
        active_session = PollSessionIndex.fetch_active_session(session, now=now)

        # return active_session.username
        return [item.username for item in active_session.username]


    def remove_player(self, session, username):
        '''
        Weird but cant invent better :c

        :param session:
        :param username:
        :return:
        '''

        # pollsession = self.fetch_active_session(session)
        player = session.query(Session2Player).filter(
            and_(Session2Player.username == username)).first()

        print(f'PLAYERS!: {player}')
        self.username.remove(player)



    @classmethod
    def fetch_exact_pollsession(cls, session, pollsession_id):
        return session.query(cls).filter(cls.session_id == pollsession_id).options(joinedload(cls.username)).one()


    # @classmethod
    # def remove_player(cls, session, username):
    #     cls.dele


    @classmethod
    def fetch_all_users_by_session_id(cls, session, session_id: int):
        try:
            one_session = session.query(cls).filter(cls.session_id == session_id).options(joinedload(cls.username)).one()
            return [item.username for item in one_session.username]
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


class Player(Base):
    __tablename__ = "players"

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String)

    score = Column(Float)
    balance = Column(Float)



engine = create_engine(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/test_data", echo=True)



from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, Time, Sequence, Date, Float

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
import datetime

from constants import PG_USER, PG_PASSWORD, PG_HOST
from sqlalchemy import select

Base = declarative_base()
metadata = MetaData()


class Session2Player(Base):
    __tablename__ = "sessions2players_orm"

    row_id = Column(Integer, autoincrement=True, primary_key=True)  # do not like but ...

    game_id = Column(Integer, ForeignKey('game_index_orm.game_id'))
    session = relationship('PollSessionIndex')
    session_id = Column(Integer, ForeignKey('session_index_orm_wide.session_id'))
    username = Column(String)
    insert_time = Column(DateTime)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.username})'


class PollSessionIndex(Base):

    __tablename__ = "session_index_orm_wide"

    session_start_time = Column(DateTime)
    session_end_time = Column(DateTime)

    session_id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    game_id = Column(Integer)
    game = relationship('GameIndex')

    team_number = Column(Integer)
    max_players_per_team = Column(Integer)
    pinned_message_id = Column(Integer)

    username = relationship(
        'Session2Player', backref='user'
    )


    def __repr__(self):
        # return f'{self.__class__.__name__}({self.session_start_time}-{self.session_end_time}): sid({self.session_id}):game_id({self.game_id}):team_number({self.team_number}):max_players_per_team({self.max_players_per_team}):pinned_message_id({self.pinned_message_id})'
        return f'{self.__class__.__name__}({self.username})'

    @classmethod
    def fetch_last_active_session_id(cls, now=datetime.datetime.now()):
        # session = Session.object_session(self)  ## does not work idk why?

        with Session(engine) as orm_session:
            return orm_session.query(cls).filter((cls.session_start_time <= now) & (cls.session_end_time >= now)).one()


    @classmethod
    def fetch_all_users_by_session_id(cls, session_id: int):
        with Session(engine) as orm_session:
            return orm_session.query(cls).filter(cls.session_id == session_id).options(joinedload(cls.username)).one()


    # username = Column('username', ForeignKey())

    # def __init__(self, session_start_time, session_end_time):
    #
    #     self.session_start_time = session_start_time
    #     self.session_end_time = session_end_time

    # def dump_myself(self):
    #     with Session(engine) as session:
    #         session.add_all([PollSessionIndex(session_start_time=self.session_start_time,
    #                                          session_end_time=self.session_end_time)])
    #         session.commit()



class GameIndex(Base):

    __tablename__ = "game_index_orm"
    game_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(ForeignKey("session_index_orm_wide.session_id"))

    session = relationship('PollSessionIndex')
    session2player = relationship('Session2Player')

    # game_date


# Association



class Player(Base):
    __tablename__ = "players"

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String)

    score = Column(Float)
    balance = Column(Float)



engine = create_engine(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/test_data", echo=True, future=True)

# if __name__ == "__main__":

    # with Session(engine) as orm_session:
    #     answer = orm_session.query(Session2Player).filter(Session2Player.session_id == 1).options(joinedload(Session2Player.session))

        # print([item.username for item in answer.all()])



        # orm_session.add_all([PollSessionIndex(session_start_time=datetime.datetime.now(),
        #                              session_end_time=datetime.datetime.now() + datetime.timedelta(days=2),
        #                              team_number=2,
        #                              max_players_per_team=9),
        #                      ])

        # orm_session.add_all([Session2Player(session_id=1, username='rvtsukanov'),
        #                      Session2Player(session_id=1, username='gasafyanov'),
        #                      Session2Player(session_id=1, username='smarchenko')])

        # orm_session.add_all([Session2Player(session_id=2, username='marbell'),
        #                      Session2Player(session_id=2, username='youknowich'),
        #                      Session2Player(session_id=2, username='sosatzenit')])
        #
        #
        #
        #
        # orm_session.commit()


    # print(obj.dump_myself())

    # with Session(engine) as session:
    # s = Session(engine)


    # for item in s.scalars(select(PollSessionIndex)):
    #     print(item)


        # session.add_all([PollSessionIndex(session_start_time=datetime.datetime.now(),
        #                                  session_end_time=datetime.datetime.now())])
        # session.commit()


    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)



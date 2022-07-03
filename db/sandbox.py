from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, Time, Sequence, Date

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
from sqlalchemy import orm

from constants import PG_USER, PG_PASSWORD, PG_HOST
from sqlalchemy import select

engine = create_engine(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/test_data", echo=False, future=True)
metadata = MetaData(engine)
Base = declarative_base(metadata=metadata)

class Team(Base):

    __tablename__ = "team"
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Player(Base):
    __tablename__ = "players"

    # def __init__(self, spent_minutes=10):
    #     self.spent_minutes = spent_minutes

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    def __repr__(self):
        return f'player_id({self.id})__first_name({self.first_name})__last_name({self.last_name})'

    # @orm.reconstructor
    # def init_on_load(self):
    #     pass

# class WhoScored(Base):
#     __tablename__ = "scores"

class Association(Base):
    __tablename__ = "association"
    player_id = Column(ForeignKey("players.id"), primary_key=True)
    team_id = Column(ForeignKey("team.id"), primary_key=True)
    player = relationship("Player")
    Team = relationship("Team")


    def __repr__(self):
        return f'player_id({self.player_id})__team_id({self.team_id})'

# who_scored_table = Table(
#     "who_scored",
#     Base.metadata,
#     Column("player_id", ForeignKey("players.id")),
#     Column("team_id", ForeignKey("team.id")),
# )



# class Scores(Base):
#     __tablename__ = "scores"
#
#     team_a =

if __name__ == "__main__":
    # with Session(engine) as session:
    #     session.add_all([Team(id=1, name='Зенит'),
    #                      Team(id=2, name='Барселона'),
    #                      Team(id=3, name='Урал'),
    #                      Team(id=4, name='Сборная России')])
    #     session.commit()

    # with Session(engine) as session:

    # conn = engine.connect()

    s = Session(engine)
    a = s.query(Association)
    # a = select(Association).filter(Association.team_id == 1).options(joinedload(Association.player))
    # a = (Association)

    print(a.all())
    # for row in conn.execute(a):
    #     print(row)
        # print(a)
        # session.add_all([Association(player_id=1, team_id=1)])
                         # Association(player_id=2, team_id=1),

        # session.commit()


    # obj = PollSessionIndex(datetime.datetime.now(), datetime.datetime.now())

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



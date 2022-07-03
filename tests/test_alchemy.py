import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import faker
import random

from db.models import Base
from constants import PG_HOST, PG_PASSWORD, PG_USER

import datetime
PG_DB = 'test_data'

from db.models import PollSessionIndex, GameIndex, Session2Player


@pytest.fixture(scope='session')
def session():
    engine = create_engine(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/test_data", echo=False, future=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Also works!
    # PollSessionIndex.__table__.create(engine)
    # GameIndex.__table__.create(engine)
    # Session2Player.__table__.create(engine)

    with Session(engine) as orm_session:
        yield orm_session

    # Base.metadata.drop_all(engine)
    # Session2Player.__table__.drop(engine)


@pytest.fixture(scope='session')
def fake():
    return faker.Faker(locale=['ru_RU'])


def insert_session_index_data(session, fake):
    num_sessions = random.randint(10, 20)

    for i in range(num_sessions):  # put abnormal session inside

        session_start_time = fake.date_time_between(start_date='-20d', end_date='-5d')
        session_end_time = fake.date_time_between(start_date=session_start_time,
                                                  end_date='-2d')

        session.add_all([PollSessionIndex(session_start_time=session_start_time,
                         session_end_time=session_end_time,
                         game_id=random.randint(1, 3),
                         team_number=random.randint(2, 3),
                         max_players_per_team=5,
                         pinned_message_id=random.randint(1, int(1e6)),
                                          game=[GameIndex()])])
    session.add_all([PollSessionIndex(session_start_time=fake.date_time_between(start_date='-1d'),
                                      session_end_time=fake.date_time_between(start_date='now', end_date='+10d'),
                                      game_id=random.randint(1, 3),
                                      team_number=random.randint(2, 3),
                                      max_players_per_team=5,
                                      pinned_message_id=random.randint(1, int(1e6))
                                      )])
    session.commit()


def insert_sessions2players_data(session, fake):

    fake = faker.Faker(locale=['ru_RU'])
    fake.user_name()

    sessions = session.query(PollSessionIndex).all()

    for sess in sessions:
        num_players = random.randint(10, 10)
        for i in range(num_players):
            session.add_all([Session2Player(session=sess,
                                           session_id=sess.session_id,
                                           username=fake.user_name(),
                                           insert_time=datetime.datetime.now())])

    session.commit()


def test_db(session, fake):
    insert_session_index_data(session, fake)
    insert_sessions2players_data(session, fake)
    assert True


def test_orm_session_index_method():
    instance = PollSessionIndex.fetch_all_users_by_session_id(5)

    # print(f'inst: {instance.username} len: {len(instance)}')
    print(f'inst: {instance} len: {len(instance.username)}')



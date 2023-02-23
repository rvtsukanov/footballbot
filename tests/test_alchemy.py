import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import faker
import random

from db.models import Base
from constants import PG_HOST, PG_PASSWORD, PG_USER

from sqlalchemy import and_

from core import find_closest_game_date

import datetime
PG_DB = 'test_data'

from db.models import PollSessionIndex, Session2Player, GameIndex, User, Transactions


# set function in order to re-create all test-cases data
@pytest.fixture(scope='function')
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


def insert_session_index_data(session, fake, players_sessions_num, add_n_active=1):
    num_sessions = len(players_sessions_num) if (not add_n_active) else (len(players_sessions_num) - add_n_active)
    session_start_time = fake.date_time_between(start_date='-100d', end_date='-99d')
    for i in range(num_sessions):  # put abnormal session inside

        session_end_time = find_closest_game_date(time=session_start_time)

        session.add_all([PollSessionIndex(session_start_time=session_start_time,
                         session_end_time=session_end_time,
                         game_id=random.randint(1, 3),
                         teams_number=random.randint(2, 3),
                         max_players_per_team=5,
                         pinned_message_id=random.randint(1, int(1e6)),
                                          game=[GameIndex()])])

        session_start_time = fake.date_time_between(start_date=session_end_time, end_date=session_end_time + datetime.timedelta(days=7))

    mapping = {}
    if add_n_active:
        for n in range(add_n_active):
            idx = num_sessions + n + 1
            session_start_time = fake.date_time_between(start_date='-2d', end_date='-1d')
            session_end_time = fake.date_time_between(start_date=session_start_time + datetime.timedelta(days=3),
                                                      end_date='+10d')
            mapping[session_start_time] = idx
            # session_end_time = find_closest_game_date(session_start_time)
            session.add_all([PollSessionIndex(session_start_time=session_start_time,
                                              session_end_time=session_end_time,
                                              game_id=random.randint(1, 3),
                                              teams_number=random.randint(2, 3),
                                              max_players_per_team=5,
                                              pinned_message_id=random.randint(1, int(1e6))
                                              )])
    session.commit()
    return mapping


def insert_sessions2players_data(session, fake, players_sessions_num):
    sessions = session.query(PollSessionIndex).all()
    mapping = {}

    for session_number, sess in enumerate(sessions):
        if session_number < len(players_sessions_num):
            num_players = players_sessions_num[session_number]
        else:
            num_players = 0

        mapping[sess.session_id] = []

        for i in range(num_players):
            username = fake.user_name()
            mapping[sess.session_id].append(username)
            session.add_all([Session2Player(session_id=sess.session_id,
                                           insert_time=datetime.datetime.now(),
                                           user=User(username=username))])
    session.commit()
    return mapping



def insert_session_with_players(session, fake):
    pollsession = PollSessionIndex(session_start_time=datetime.datetime.now() - datetime.timedelta(7),
                     session_end_time=datetime.datetime.now() + datetime.timedelta(7),
                     game_id=random.randint(1, 3),
                     teams_number=random.randint(2, 3),
                     max_players_per_team=104,
                     pinned_message_id=random.randint(1, int(1e6))
                     )

    pollsession.users = [User(username=f'galya_{i}') for i in range(100)]

    session.add_all([pollsession])
    session.commit()



def insert_user_data(session, fake, n=5):
    for _ in range(n):
        name = fake.user_name()
        # print('name is ', name)
        session.add_all([User(username=name)])
    session.commit()


def test_user_table(session, fake):
    insert_user_data(session, fake)
    assert len(session.query(User).all()) == 5


def test_mapper(session, fake):
    insert_session_with_players(session, fake)
    active_session = PollSessionIndex.fetch_active_session(session, datetime.datetime.now())

    print(active_session.users)


def test_transactions(session, fake):
    our_user = User(username=f'petya')
    extra_user = User(username='vasya')

    trans1 = Transactions(user=our_user, description='Зачисление на баланс', amount=1200)
    trans2 = Transactions(user=our_user, description='Игра (10/09/22)', amount=-650)
    trans3 = Transactions(user=our_user, description='Штраф', amount=-100)
    trans4 = Transactions(user=extra_user, description='Штраф', amount=-500)

    # print('RESULT: ', sum([trans1, trans2, trans3]))

    session.add_all([trans1, trans2, trans3, trans4])
    session.commit()

    assert our_user.get_balance(session) == 450


# each players_sessions_num is a number of players in a corresponding session_id (by its index)
@pytest.mark.parametrize('players_sessions_num, add_n_active, is_random_session_id',
                         [([5, 5, 3, 0, 1], 1, True),
                          ([5, 5, 3, 0, 1], 0, 7),
                          ([0, 2, 3, 0, 0], 1, True)])
def test_fetch_all_users_by_session_id(fake, session, players_sessions_num, add_n_active, is_random_session_id):
    insert_session_index_data(session, fake, players_sessions_num, add_n_active)
    mapping = insert_sessions2players_data(session, fake, players_sessions_num)
    if is_random_session_id:
        session_id = random.randint(1, max(mapping.keys()))
    else:
        session_id = is_random_session_id
    users = PollSessionIndex.fetch_all_users_by_session_id(session, session_id)
    assert users == mapping[session_id]


@pytest.mark.parametrize('players_sessions_num, add_n_active',
                         [([3] * 5, 1),
                          ([3] * 5, 2),
                          ([3] * 5, 0)])
def test_fetch_last_active_session_id(session, fake, players_sessions_num, add_n_active):
    mapping = insert_session_index_data(session, fake, players_sessions_num, add_n_active)
    if mapping:
        idx = mapping[sorted(mapping, reverse=True)[0]]
    session_id = PollSessionIndex.fetch_last_active_session_id(session,
                                                               datetime.datetime.now())
    if add_n_active:
        assert session_id.session_id == idx
    else:
        assert session_id == 0


def test_modify_session(session, fake):
    insert_session_index_data(session, fake, [3] * 5, 1)
    active_session = PollSessionIndex.fetch_last_active_session_id(session,
                                                                   datetime.datetime.now())

    active_session._modify_session(session, attribute='max_players_per_team', new_value=10)

    assert active_session.max_players_per_team == 10


def test_add_players(session, fake):
    insert_session_index_data(session, fake, players_sessions_num=[3] * 5, add_n_active=1)

    active_session = PollSessionIndex.fetch_active_session(session, datetime.datetime.now())
    active_session.add_player(session, User(username='pupkin'))

    assert 'pupkin' in PollSessionIndex.fetch_all_users_by_session_id(session, active_session.session_id)



def test_remove_players(session, fake):
    insert_session_index_data(session, fake, players_sessions_num=[3] * 5, add_n_active=1)
    # insert_sessions2players_data(session, fake, [3] * 5)
    pollsession = PollSessionIndex.fetch_exact_pollsession(session, 1)
    pollsession.add_player(session, User(username='pupkin'))
    pollsession.add_player(session, User(username='pupkin'))

    assert 'pupkin' in PollSessionIndex.fetch_all_users_by_session_id(session, pollsession.session_id)
    pollsession.remove_player(session, user=User(username='pupkin'))
    assert 'pupkin' not in PollSessionIndex.fetch_all_users_by_session_id(session, pollsession.session_id)



def test_sorting_order(session, fake):
    insert_session_index_data(session, fake, players_sessions_num=[3] * 5, add_n_active=1)
    insert_sessions2players_data(session, fake, [3] * 5)
    active_session = PollSessionIndex.fetch_active_session(session, datetime.datetime.now())
    print(active_session.get_current_list_of_players(session))


def test_max_restrictions(session, fake):
    insert_session_index_data(session, fake, players_sessions_num=[3] * 5, add_n_active=1)
    active_session = PollSessionIndex.fetch_active_session(session, datetime.datetime.now())

    max_players_per_team = active_session.max_players_per_team

    for _ in range(max_players_per_team + 5):
        active_session.add_player(session, User(username=fake.user_name()))

    assert max_players_per_team == len(active_session.users)


def test_zero_level(session, fake):

    insert_session_index_data(session, fake, players_sessions_num=[3] * 5, add_n_active=1)
    insert_sessions2players_data(session, fake, [3] * 5)

    active_session = PollSessionIndex.fetch_active_session(session, datetime.datetime.now())

    assert len(active_session.users) > 0

    # for user in active_session.get_current_list_of_players(session):
    all_users = active_session.users
    print(len(active_session.users))
    print(all_users)
    for user in all_users:
        print(user)
        active_session.remove_player(session, user)

    # active_session.remove_player(session, user)

    assert len(active_session.users) == 0












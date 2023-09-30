import datetime

from footballbot.extensions import db
from footballbot.models.pollsession import Pollsession
from footballbot.models.player import Player
from footballbot.models.pollsession2player import Pollsession2Player
from footballbot.models.transactions import Transaction
import faker
import time



def fake_n_players(n: int):
    fake = faker.Faker(locale=['ru_RU'])
    for _ in range(n):
        yield Player(player_id=fake.random.randint(1, 1e7), telegram_name=f'@{fake.user_name()}')

# fake.date_time_between(start_date='-100d', end_date='-99d')

def make_scenario_1(app):
    '''
    Scenario #1 <Check player duplicates in one session are allowed>
    - Step 1: Making active pollsession with infinite number of players
    - Step 2: Add 5 random players
    - Step 3: Choosing last added player; sleep 2 sec (for re-setting insert time); add last player again

    Positive outline:
    - Duplicated players are in secondary table
    - Removing players is correct considering number of "overbooking"
    '''
    with app.app_context():
        db.create_all()
        ps = Pollsession(teams_number=3,
                         max_players_per_team=10)

        for p in fake_n_players(4):
            ps.player_votes.append(Pollsession2Player(player=p))

        time.sleep(2)

        for p in fake_n_players(1):
            ps.player_votes.append(Pollsession2Player(player=p))

        db.session.add(ps)
        db.session.commit()

        time.sleep(2)

        ps.player_votes.append(Pollsession2Player(player=p))
        db.session.commit()


def make_scenario_2(app):
    '''
    Scenario #2 <Check if it is possible to add player violating session maximum>
    - Step 1: creating pollsession with maximum 1 player
    - Step 2: trying to add another player

    Positive outline:
    - Raising exception with the message of violating the maximum.
    '''
    with app.app_context():
        db.create_all()

        ps = Pollsession(teams_number=1,
                         max_players_per_team=1)

        for p in fake_n_players(1):
            ps.player_votes.append(Pollsession2Player(player=p))

        db.session.add(ps)
        db.session.commit()


def make_scenario_3(app):
    '''
    Scenario #3 <TODO>

    Positive outline:
    '''
    with app.app_context():
        db.create_all()

        transactions = []

        for n, p in enumerate(fake_n_players(10)):
            for k in range(2):
                transactions.append(Transaction(player=p, amount=n ** 2))
                transactions.append(Transaction(player=p, amount=-n ** 2))

        db.session.add_all(transactions)
        db.session.commit()


def make_scenario_4(app):
    p1 = Player(player_id=123, telegram_name='@abc', role='admin', secret='ABC')
    p2 = Player(player_id=456, telegram_name='@def', role='admin', secret='XYZ')
    p3 = Player(player_id=789, telegram_name='@xyz', role='player', secret='EDF')

    with app.app_context():
        db.create_all()
        db.session.add_all([p1, p2, p3])
        db.session.commit()


def make_scenario_5(app):
    '''
    Scenario #5 <Check if active pollsessions work properly>

    Positive outline:

    '''
    with app.app_context():
        db.create_all()

        now = datetime.datetime.now()
        left = now - datetime.timedelta(days=3)
        right = now + datetime.timedelta(days=3)

        ps_old = Pollsession(teams_number=2,
                         max_players_per_team=5,
                         creation_dt=datetime.datetime(2021, 1, 1),
                         matchtime_dt=datetime.datetime(2021, 1, 5))

        ps_active = Pollsession(teams_number=2,
                             max_players_per_team=5,
                             creation_dt=left,
                             matchtime_dt=right)

        db.session.add_all([ps_old, ps_active])
        db.session.commit()

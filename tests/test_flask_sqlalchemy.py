import time

import pytest
import os
from footballbot.extensions import db
from footballbot.models.player import Player
from footballbot.models.pollsession import Pollsession
from footballbot.models.transactions import Transaction
from tests.app_builder import app_scenario_1, app_scenario_2, app_scenario_3, app_scenario_4, app_scenario_5, client

@pytest.fixture
def client(app_scenario_1):
    return app_scenario_1.test_client()


def test_serialization(app_scenario_1):
    with app_scenario_1.app_context():
        p = Player(player_id=234, telegram_name='@123')
        keys = p.to_dict().keys()
    assert 'player_id' in keys and 'telegram_name' in keys


def test_transactions_sums(app_scenario_3):
    with app_scenario_3.app_context():
        players = db.session.query(Player).all()
        s = []
        for player in players:
            s.append(player.sum_up_all_transactions())
        assert sum(s) == 0


def test_transactions_sums(app_scenario_3):
    with app_scenario_3.app_context():
        t = db.session.query(Transaction).first()
        td = t.to_dict()
        pass


def test_serialization_via_serializer(app_scenario_1):
    with app_scenario_1.app_context():
        p = Player(player_id=234, telegram_name='@123')
        d = p.to_dict()
        ps = Pollsession(teams_number=3,
                         max_players_per_team=1,
                         pinned_message_id=100)

        ps.add_player(p)
        db.session.add(ps)
        db.session.commit()

        lps = Pollsession.fetch_last_pollsession().to_dict()

        assert len(lps['player_votes']) > 0


def test_scenario_1(app_scenario_1, client):
    with app_scenario_1.app_context():
        last_pollsession = Pollsession.fetch_last_pollsession()
        votes_sorted = last_pollsession.player_votes

        last_vote = sorted(votes_sorted)[-1]
        telegram_name_of_deleted_player = last_vote.player.telegram_name

        db.session.delete(last_vote)
        db.session.commit()

        assert len(last_pollsession.player_votes_rendered) == 5

        players_sorted = last_pollsession.player_votes_rendered
        pre_last_player = sorted(players_sorted)[-1]

        db.session.delete(pre_last_player)
        db.session.commit()

        # last_pollsession = Pollsession.fetch_last_pollsession()
        assert len(last_pollsession.player_votes_rendered) == 4
        assert telegram_name_of_deleted_player not in \
               [vote.player.telegram_name for vote in last_pollsession.player_votes_rendered]


def test_scenario_1_delete_player(app_scenario_1):
    with app_scenario_1.app_context():
        last_pollsession = Pollsession.fetch_last_pollsession()
        player = last_pollsession.get_lastly_added_player()
        assert isinstance(player, Player)
        last_pollsession.delete_player(player)


def test_scenario_1_delete_nonexisting_player(app_scenario_1):
    with app_scenario_1.app_context():
        last_pollsession = Pollsession.fetch_last_pollsession()
        player = Player(telegram_name='@nonexisingplayer', player_id=234)
        db.session.add(player)
        db.session.commit()

        with pytest.raises(ValueError):
            last_pollsession.delete_player(player)


def test_scenario_1_add_player(app_scenario_1):
    with app_scenario_1.app_context():
        last_pollsession = Pollsession.fetch_last_pollsession()
        telegram_names = last_pollsession.get_players_telegram_names()
        player = Player.find_player(telegram_name=telegram_names[0])
        last_pollsession.add_player(player)
        last_added_player = last_pollsession.get_lastly_added_player()
        assert player == last_added_player


def test_scenario_2_add_player_with_max(app_scenario_2):
    with app_scenario_2.app_context():
        last_pollsession = Pollsession.fetch_last_pollsession()
        player = last_pollsession.get_lastly_added_player()

        with pytest.raises(ValueError):
            last_pollsession.add_player(player)


def test_transactions(app_scenario_2):
    with app_scenario_2.app_context():
        p1 = Player(player_id=345)
        p2 = Player(player_id=300)

        t1 = Transaction(player=p1, amount=100)
        time.sleep(2)
        t2 = Transaction(player=p1, amount=-70)

        t3 = Transaction(player=p2, amount=777)

        db.session.add_all([t1, t2, t3])
        db.session.commit()

        trans = p1.get_last_n_transactions(1)
        s1 = p1.sum_up_all_transactions()
        s2 = p2.sum_up_all_transactions()

        assert s1 == 30
        assert s2 == 777
        assert len(trans) == 1


def test_transactions_inside_pollsessions(app_scenario_2):
    with app_scenario_2.app_context():
        p1 = Player(player_id=345)
        p2 = Player(player_id=300)
        p3 = Player(player_id=500)

        ps = Pollsession(teams_number=2,
                         max_players_per_team=5,
                         )

        for p in [p1, p2, p2]:
            ps.add_player(p)

        ps.calculate_pollsession(3333)

        assert p2.sum_up_all_transactions() == -2222
        assert p1.sum_up_all_transactions() == -1111
        assert p3.sum_up_all_transactions() == 0


def test_auth(app_scenario_4, client):
    with app_scenario_4.app_context():
        with client:
            # "ABC" is correct key is existing in Player table while "AAA" - do not
            response = client.get("/test", headers={'Authorization': 'Bearer ABC'}, data={})
            assert response.status_code == 200

            response = client.get("/test", headers={'Authorization': 'Bearer AAA'}, data={})
            assert response.status_code == 401

            response = client.get("/test", headers={'Authorization': 'Bearer EDF'}, data={})
            assert response.status_code == 403


def test_active_pollsessions(app_scenario_5):
    with app_scenario_5.app_context():
        pollsession = Pollsession.fetch_active_pollsession()
        assert pollsession is not None

        pollsession.add_player(Player(player_id=15))
        pollsession.delete()

        ans = Pollsession.check_if_active_exists()
        assert not ans


def test_pollsession_calculation(app_scenario_5):
    with app_scenario_5.app_context():
        pollsession = Pollsession.find_pollsession_by_id(1)
        p = Player(player_id=123)
        pollsession.add_player(p)
        pollsession.calculate_pollsession(total_amount=1000)

        active_pollsession = Pollsession.fetch_active_pollsession()

        with pytest.raises(ValueError):
            active_pollsession.calculate_pollsession(total_amount=1000)

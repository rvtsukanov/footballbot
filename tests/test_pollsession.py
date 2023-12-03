from tests.app_builder import app_scenario_1
from footballbot.models.player import Player
from footballbot.models.pollsession import Pollsession


def test_get_lastly_added_n_players(app_scenario_1):
    with app_scenario_1.app_context():
        active_pollsession = Pollsession.fetch_active_pollsession()
        # last_players = active_pollsession.get_lastly_added_n_players(5)
        active_pollsession.decrease_num_players_by_n(3)


def test_increase_num__by_n(app_scenario_1):
    with app_scenario_1.app_context():
        active_pollsession = Pollsession.fetch_active_pollsession()
        active_pollsession.increase_num_players_by_n(3)
    pass
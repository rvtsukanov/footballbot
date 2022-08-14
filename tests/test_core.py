from scenarios import MessageScenario
from core import find_closest_game_date
import pytest
import datetime


@pytest.mark.parametrize('condition_1, condition_2, final_argument, result',
                         [(lambda x: x > 3, lambda x: x < 5, 4, True),
                          (lambda x: x > 3, lambda x: x < 5, 1, False),
                          (lambda x: x > 3, lambda x: x < 5, 10, False)])
def test_and_operator(condition_1, condition_2, final_argument, result):
    ms1 = MessageScenario(condition_1)
    ms2 = MessageScenario(condition_2)
    ms3 = ms1 & ms2

    assert ms3(final_argument) == result


@pytest.mark.parametrize('condition_1, condition_2, final_argument, result',
                         [(lambda x: x < 3, lambda x: x > 5, 4, False),
                          (lambda x: x > 3, lambda x: x < 5, 1, True),
                          (lambda x: x > 3, lambda x: x < 5, 10, True)])
def test_or_operator(condition_1, condition_2, final_argument, result):
    ms1 = MessageScenario(condition_1)
    ms2 = MessageScenario(condition_2)
    ms3 = ms1 | ms2

    assert ms3(final_argument) == result



@pytest.mark.parametrize('time, matchday, matchtime, result', [(datetime.datetime(2022, 7, 8, 9, 0),
                                                    5,
                                                    datetime.time(11, 0),
                                                    datetime.datetime(2022, 7, 9, 13, 0)),

                                                    (datetime.datetime(2022, 7, 10, 9, 0),
                                                    5,
                                                    datetime.time(11, 0),
                                                    datetime.datetime(2022, 7, 16, 13, 0)),

                                                    (datetime.datetime(2022, 7, 9, 10, 59),
                                                    5,
                                                    datetime.time(11, 0),
                                                    datetime.datetime(2022, 7, 9, 13, 0)),

                                                    (datetime.datetime(2022, 7, 9, 11, 0),
                                                    5,
                                                    datetime.time(11, 0),
                                                    datetime.datetime(2022, 7, 16, 13, 0))
                                                    ])
def test_find_closest_game_date(time, matchday, matchtime, result):
    assert result == find_closest_game_date(time, matchday=matchday, matchtime=matchtime, hours_offset=2)

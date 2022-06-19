from scenarios import MessageScenario
import pytest


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

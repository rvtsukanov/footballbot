import time

import pytest
import os
from footballbot.extensions import db
from tests.app_builder import app_scenario_1, app_scenario_2, app_scenario_3, app_scenario_4


def test_authq(app_scenario_4, client):
    with app_scenario_4.app_context():
        with client:
            # "ABC" is correct key is existing in Player table while "AAA" - do not
            response = client.get("/init_response", headers={'Authorization': 'Bearer ABC'}, data={})
            assert response.status_code == 200
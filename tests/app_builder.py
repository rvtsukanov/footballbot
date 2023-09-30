import pytest
import os
from footballbot import create_app
from tests.scenarios import make_scenario_1, make_scenario_2, make_scenario_3, make_scenario_4, make_scenario_5
from footballbot.extensions import db

def build_scenario(scenario_maker):
    # @pytest.fixture(scope='function')
    @pytest.fixture
    def app_scenario():
        basedir = os.path.abspath(os.path.dirname(__file__))
        uri = 'sqlite:///' + os.path.join(basedir, 'local.db')
        print(uri)

        app = create_app()
        app.config.update({
            "SQLALCHEMY_DATABASE_URI": uri,
            "TESTING": True,
            "DEBUG": True
        })
        with app.app_context():
            db.create_all()
        scenario_maker(app)
        yield app
        with app.app_context():
            db.drop_all()

    return app_scenario


app_scenario_1 = build_scenario(make_scenario_1)
app_scenario_2 = build_scenario(make_scenario_2)
app_scenario_3 = build_scenario(make_scenario_3)
app_scenario_4 = build_scenario(make_scenario_4)
app_scenario_5 = build_scenario(make_scenario_5)

@pytest.fixture
def client(app_scenario_4):
    return app_scenario_4.test_client()

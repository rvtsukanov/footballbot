from flask import Flask

from db.models import PollSessionIndex
from sqlalchemy import create_engine
from constants import PG_HOST, PG_PASSWORD, PG_USER
from sqlalchemy.orm import Session
from flask import request
from flask import jsonify
import datetime


engine = create_engine(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/test_data", echo=False)
session = Session(engine)

app = Flask(__name__)

@app.route('/getCurrentListOfPlayers')
def index():
    players = PollSessionIndex.get_current_list_of_players(session)
    return {'players': players}


@app.route('/addPlayerToCurrentSession/<username>')
def add_player_to_current_session(username):
    active_session = PollSessionIndex.fetch_last_active_session_id(session,
                                                                   datetime.datetime.now())
    active_session.add_player(session, username)
    return jsonify(success=True)


@app.route('/removePlayerFromCurrentSession/<username>')
def remove_player_from_current_session(username):
    active_session = PollSessionIndex.fetch_last_active_session_id(session,
                                                                   datetime.datetime.now())

    active_session.remove_player(session, username)

    return jsonify(success=True)





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
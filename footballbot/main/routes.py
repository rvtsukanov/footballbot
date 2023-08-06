from footballbot.main import bp
from flask import Response
from flask import request

from footballbot.models.pollsession import Pollsession
from footballbot.models.pollsession2player import pollsession2player
from footballbot.models.player import Player
from footballbot.extensions import db

@bp.route('/fetch_last_pollsession')
def fetch_last_pollsession():
    last_pollsession = Pollsession.fetch_last_pollsession()
    db.session.query(Pollsession)
    print(last_pollsession.players)
    return '200'



@bp.route('/create_new_pollsession')
def create_new_pollsession():
    teams_number = request.args.get('teams_number', default=2)
    max_players_per_team = request.args.get('max_players_per_team', default=9)
    pinned_message_id = request.args.get('pinned_message_id', default=None)
    pollsession = Pollsession(teams_number=teams_number,
                              max_players_per_team=max_players_per_team,
                              pinned_message_id=pinned_message_id)

    db.session.add(pollsession)
    db.session.commit()
    return Response(status=200)


@bp.route('/register_new_player')
def register_new_player():
    player_id = request.args.get('player_id')
    telegram_name = request.args.get('telegram_name')
    player = Player(player_id=player_id, telegram_name=telegram_name)
    db.session.add(player)
    db.session.commit()
    return Response(status=200)


@bp.route('/add_player_to_last_pollsession')
def add_player_to_last_pollsession():
    player_id = request.args.get('player_id')
    player = Player.find_player(player_id=int(player_id))
    last_pollsession = Pollsession.fetch_last_pollsession()

    # Validate if it is possible
    last_pollsession.players.append(player)
    db.session.commit()

    return '200'

@bp.route('/remove_player_from_last_pollsession/<player_id>')
def remove_player_from_last_pollsession(player_id):
    player = Player.find_player(player_id=int(player_id))
    last_pollsession = Pollsession.fetch_last_pollsession()

    # pollsession2player

    last_pollsession.players.remove(player)
    db.session.commit()

    return Response(status=200)



@bp.route('/modify_pollsession')
def modify_pollsession():
    max_players_per_team = request.args.get('max_players_per_team', default=9)



@bp.route('/apocalypse')
def apocalypse():
    '''
    Drop all data from all databases
    Use for debug and migration purposes
    '''
    db.drop_all()
    return Response(status=200)

@bp.route('/initdb')
def initdb():
    '''
    Create databases
    Use for debug and migration purposes
    '''
    try:
        db.create_all()
        return Response(status=200)
    except:
        return Response(status=404)
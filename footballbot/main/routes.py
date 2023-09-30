import os

from footballbot.main import bp
from flask import Response
from flask import request, jsonify

from footballbot.models.pollsession import Pollsession
from footballbot.models.pollsession2player import Pollsession2Player
from footballbot.models.transactions import Transaction
from footballbot.models.player import Player
from footballbot.extensions import db, auth
import hashlib


@auth.verify_token
def verify_secret(secret):
    player = Player.verify_token(secret)
    if player:
        return player


@auth.get_user_roles
def get_user_roles(player):
    role = player.get_role()
    return role

@bp.route('/test')
@auth.login_required(role='admin')
def ps():
    return str(auth.current_user())


@bp.route('/fetch_last_pollsession')
@auth.login_required(role=['player', 'admin'])
def fetch_last_pollsession():
    last_pollsession = Pollsession.fetch_last_pollsession()
    return jsonify(last_pollsession.to_dict())


@bp.route('/create_new_player', methods=['POST'])
@auth.login_required(role='admin')
def create_new_player():
    player_id = request.values.get('player_id')
    if not player_id:
        return Response(response='player_id should be presented.', status=400)

    player = Player.find_player(player_id=player_id)
    if player:
        return Response(response=f'Player {player_id} already exist.', status=400)
    else:
        telegram_name = request.values.get('telegram_name')
        role = request.values.get('role', default='player')

        secret_string = str(player_id) + str(os.environ.get('SECRET_KEY'))
        secret = hashlib.sha256(secret_string.encode(encoding='utf-8')).hexdigest()

        player = Player(player_id=player_id, telegram_name=telegram_name, role=role,
                   secret=secret)

        db.session.add(player)
        db.session.commit()

        return player.to_dict()


@bp.route('/create_new_pollsession', methods=['POST'])
@auth.login_required(role='admin')
def create_new_pollsession():
    if Pollsession.check_if_active_exists():
        return Response(response=f'Active session already exists. Join or call /destroy_active_session endpoint.',
                        status=400)
    else:
        teams_number = request.values.get('teams_number', default=2)
        max_players_per_team = request.values.get('max_players_per_team', default=9)
        pinned_message_id = request.values.get('pinned_message_id', default=None)

        pollsession = Pollsession(teams_number=teams_number,
                                  max_players_per_team=max_players_per_team,
                                  pinned_message_id=pinned_message_id)

        db.session.add(pollsession)
        db.session.commit()
        return pollsession.to_dict()


@bp.route('/register_new_player')
@auth.login_required(role='admin')
def register_new_player():
    player_id = request.values.get('player_id')
    telegram_name = request.values.get('telegram_name')
    player = Player(player_id=player_id, telegram_name=telegram_name)
    db.session.add(player)
    db.session.commit()
    return Response(status=200)


@bp.route('/add_player_to_active_pollsession', methods=['POST'])
@auth.login_required(role='admin')
def add_player_to_active_pollsession():
    player_id = request.values.get('player_id')
    telegram_name = request.values.get('telegram_name')

    player = Player.find_player(player_id=int(player_id), telegram_name=telegram_name)
    if not player:
        return Response(response=f'Player {telegram_name} not found. Create instance first', status=400)
    elif not Pollsession.check_if_active_exists():
        return Response(response=f'Active session not found. Create it first.', status=400)
    else:
        active_pollsession = Pollsession.fetch_active_pollsession()
        active_pollsession.add_player(player)
        return active_pollsession.to_dict()

@bp.route('/remove_player_from_active_pollsession', methods=['POST'])
@auth.login_required(role='admin')
def remove_player_from_last_pollsession():
    player_id = request.values.get('player_id')
    telegram_name = request.values.get('telegram_name')
    player = Player.find_player(player_id=int(player_id), telegram_name=telegram_name)
    if not player:
        return Response(response=f'Player {telegram_name} not found. Create instance first', status=400)
    elif not Pollsession.check_if_active_exists():
        return Response(response=f'Active session not found. Create it first.', status=400)
    else:
        active_pollsession = Pollsession.fetch_active_pollsession()
        active_pollsession.delete_player(player)
        return active_pollsession.to_dict()


@bp.route('/destroy_active_session', methods=['POST'])
@auth.login_required(role='admin')
def destroy_active_session():
    if not Pollsession.check_if_active_exists():
        return Response(response=f'Active session not found. Create it first.', status=400)
    else:
        active_pollsession = Pollsession.fetch_active_pollsession()
        active_pollsession.delete()
        return Response(status=200)


@bp.route('/calculate_pollsession', methods=['POST'])
@auth.login_required(role='admin')
def calculate_pollsession():
    pollsession_id = int(request.values.get('pollsession_id'))
    total_amount = float(request.values.get('total_amount'))
    pollsession = Pollsession.find_pollsession_by_id(pollsession_id)

    try:
        pollsession.calculate_pollsession(total_amount=total_amount)
        return Response(status=200)

    except ValueError:
        return Response(response='Session is active or already calculated.', status=400)


@bp.route('/add_custom_transaction', methods=['POST'])
@auth.login_required(role='admin')
def add_custom_transaction():
    player_id = request.values.get('player_id')
    amount = request.values.get('amount')
    description = request.values.get('description', default='')
    player = Player.find_player(player_id=player_id)
    if not player:
        return Response(response=f'Player {player_id} not found. Create instance first', status=400)
    else:
        t = Transaction(player=player, amount=amount, description=description)
        t.add_transaction()
        return t.to_dict()

@bp.route('/fetch_last_transactions', methods=['GET'])
@auth.login_required(role=['player', 'admin'])
def fetch_last_transactions():
    player_id = request.values.get('player_id')
    n_last = request.values.get('n_last')
    if not player_id:
        player = auth.current_user()
    else:
        player = Player.find_player(player_id=player_id)

    transactions = player.get_last_n_transactions(n_last)
    print(transactions)
    return jsonify([t.to_dict() for t in transactions])


@bp.route('/get_current_amount', methods=['GET'])
@auth.login_required(role=['player', 'admin'])
def get_current_amount():
    player_id = request.values.get('player_id')
    if not player_id:
        player = auth.current_user()
    else:
        player = Player.find_player(player_id=player_id)
    return jsonify(player.sum_up_all_transactions())

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
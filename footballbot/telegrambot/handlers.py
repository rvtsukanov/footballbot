import flask
import requests

from footballbot.extensions import db, fsa
from config import BaseConfig
from footballbot.models.pollsession import Pollsession
from footballbot.models.player import Player
from flask import redirect, url_for
import telebot
from footballbot.telegrambot.plus_minus_markup import make_plus_minus_markup
import os
import hashlib
from footballbot.telegrambot.decorators import admin_only

from footballbot import app
config = app.config

from footballbot.extensions import bot

@bot.message_handler(commands=['get_ps_https'])
def get_ps(message):
    with app.app_context():
        telegram_player = Player.find_player(player_id='0')
        print(f'message is: {message}')

        response = requests.get('https://127.0.0.1:5000/fetch_last_pollsession',
                                headers={'Content-Type': 'application/x-www-form-urlencoded',
                                         'Authorization': f'Bearer {telegram_player.secret}'},
                                data={},
                                verify=False)

        json = response.json()
        print([p['player']['telegram_name'] for p in json['player_votes']])

        bot.send_message(message.chat.id, '\n'.join([p['player']['telegram_name'] for p in json['player_votes']]))

@bot.message_handler(commands=['pollstatus'])
# @admin_only
def pollstatus(message):
    with app.app_context():
        active_session = Pollsession.fetch_active_pollsession()
        if active_session:
            bot.reply_to(message=message, text=f'active_session is {active_session.pollsession_id} \n\n {active_session.render()}')
        else:
            bot.reply_to(message=message,
                         text=f'Session not found. Create it first.')


@bot.message_handler(commands=['register'])
def register_player(message):
    with app.app_context():
        player = Player.find_player(player_id=message.from_user.id)

        if not player:
            secret_string = str(message.from_user.id) + str(os.environ.get('SECRET_KEY'))
            secret = hashlib.sha256(secret_string.encode(encoding='utf-8')).hexdigest()

            db.session.add(Player(player_id=message.from_user.id,
                                  telegram_name=message.from_user.username,
                                  secret=secret))
            db.session.commit()
            bot.reply_to(message=message, text=f'<b>Player is created.\nYour secret key is {secret}. ' +
                                               f'Use it for auth in doweplayfootball.ru site</b>')

        else:
            bot.reply_to(message=message, text=f'Player {player.telegram_name} (id {player.player_id}) already exists.')


@bot.message_handler(commands=['destroy_active_session'])
@admin_only
def destroy_active_session(message):
    with app.app_context():
        if not Pollsession.check_if_active_exists():
            return bot.reply_to(message=message, text=f'Active session not found. Create it first.')
        else:
            active_pollsession = Pollsession.fetch_active_pollsession()
            active_pollsession.delete()
            return bot.reply_to(message=message,
                                text=f'Session with id={active_pollsession.pollsession_id} created at {active_pollsession.creation_dt} is deleted successfully.')


@bot.message_handler(commands=['create_new_pollsession'])
def create_new_pollsession(message):
    message_id = message.message_id
    with app.app_context():
        if Pollsession.check_if_active_exists():
            return bot.reply_to(message=message, text=f'Active session already exists.' +
                                                      f' Join or call /destroy_active_session endpoint.')
        else:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row_width = 3
            markup.add(
                telebot.types.InlineKeyboardButton("2", callback_data="2"),
                telebot.types.InlineKeyboardButton("3", callback_data="3"),
                telebot.types.InlineKeyboardButton("4", callback_data="4"),
            )
            bot.reply_to(message=message,
                         text='Choose num_teams for following pollsession from markup or type manually.',
                         reply_markup=markup)
            # fsa[message.chat.id] = {'create_new_pollsession': 1}
            fsa['create_new_pollsession'] = {}


@bot.message_handler(commands=['decrease_players_num'])
def decrease_players_num(message):
    if Pollsession.check_if_active_exists():
        active_pollsession = Pollsession.fetch_active_pollsession()
        # active_pollsession




@bot.callback_query_handler(func=lambda call: "Голосование" in call.message.text)
def callback_query(call):
    player_id = call.from_user.id
    with app.app_context():
        pollsession = Pollsession.find_pollsession_by_message(call.message.id)
        player = Player.find_player(player_id=player_id)
        if "+" in call.data:
            pollsession.add_player(player)
            db.session.commit()
            bot.edit_message_text(text=pollsession.render(), chat_id=config['GROUP_ID'],
                                  message_id=pollsession.pinned_message_id,
                                  reply_markup=make_plus_minus_markup())
        elif "-" in call.data:
            pollsession.delete_player(player)
            db.session.commit()
            bot.edit_message_text(text=pollsession.render(), chat_id=config['GROUP_ID'],
                                  message_id=pollsession.pinned_message_id, reply_markup=make_plus_minus_markup())

        elif 'Calculate' in call.data:
            player = Player.find_player(player_id=player_id)
            if player.get_role() == 'admin':
                pollsession.calculate_pollsession(config['GAME_COST'])
                bot.edit_message_text(text=pollsession.render(), chat_id=config['GROUP_ID'],
                                      message_id=pollsession.pinned_message_id, reply_markup=make_plus_minus_markup(activate=False))


@bot.callback_query_handler(func=lambda call: 'Choose num_teams for' in call.message.text)
def callback_create_pollsession_num_teams(call):
    fsa['create_new_pollsession'] = {'teams_number': call.data}

    rng_players_per_team_map = {2: [10, 12, 14, 16, 18, 20],
                                3: [12, 15, 18, 21],
                                4: [12, 16, 20]}

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(*[telebot.types.InlineKeyboardButton(num,
                                                    callback_data=num) for num in rng_players_per_team_map[int(call.data)]])

    bot.reply_to(message=call.message,
                 text=f'{call.data} teams were chosen. Now, choose number_players via inline keyboard or type manually.',
                 reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'number_players' in call.message.text)
def callback_create_pollsession_num_players(call):
    with app.app_context():
        fsa['create_new_pollsession'].update({'num_players': call.data})
        print(fsa)

        teams_number = fsa['create_new_pollsession']['teams_number']
        max_players_per_team = int(fsa['create_new_pollsession']['num_players']) / int(teams_number)

        pollsession = Pollsession(teams_number=teams_number,
                                  max_players_per_team=max_players_per_team)


        db.session.add(pollsession)
        db.session.commit()

        created_pollsession = Pollsession.fetch_active_pollsession()

        bot.reply_to(message=call.message,
                     text=f'Session with <b>id={created_pollsession.pollsession_id}</b> created at {created_pollsession.creation_dt}\n' +
                          f'Number of teams is {pollsession.teams_number}\nTotal number of players is {pollsession.max_players}')

        sended_msg = bot.send_message(config['GROUP_ID'], pollsession.render(), reply_markup=make_plus_minus_markup())

        bot.pin_chat_message(sended_msg.chat.id, sended_msg.message_id)

        pollsession.pinned_message_id = sended_msg.message_id
        db.session.commit()


# @bot.message_handler(commands=['calculate_pollsession'])
# def calculate_pollsession():
#
#     pollsession_id = int(request.values.get('pollsession_id'))
#     total_amount = float(request.values.get('total_amount'))
#     pollsession = Pollsession.find_pollsession_by_id(pollsession_id)
#
#     try:
#         pollsession.calculate_pollsession(total_amount=total_amount)
#         return Response(status=200)
#
#     except ValueError:
#         return Response(response='Session is active or already calculated.', status=400)

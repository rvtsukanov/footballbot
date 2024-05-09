import logging

from footballbot.extensions import bot
from footballbot.telegrambot.states import StartPollsessionStates, ModifyPollsessionStates
from footballbot.telegrambot.callback_factories import num_players_factory, num_teams_factory
import telebot
from footballbot import app
from footballbot.telegrambot.markups import make_plus_minus_markup, make_num_players_markup

config = app.config

from footballbot.models.pollsession import Pollsession
from footballbot.extensions import db

@bot.callback_query_handler(func=None, state=StartPollsessionStates.num_teams, config=num_teams_factory.filter())
def callback_create_pollsession_num_teams(call):
    '''
    | CREATE-POLLSESSION PIPELINE: STEP 1 (BUTTON) |
    Revokes by: /create_pollsession's markup button pressure
    Do: loads info from pressed markup button, reset state to StartPollsessionStates.num_players
    '''

    with bot.retrieve_data(call.from_user.id) as data:
        data['num_teams'] = call.data.split(':')[1]
        num_players = data['num_teams']

    bot.reply_to(message=call.message,
                 text=f'{num_players} teams were chosen. Now, choose number_players via inline keyboard or type manually.',
                 reply_markup=make_num_players_markup(num_players))
    bot.set_state(call.from_user.id, StartPollsessionStates.num_players, chat_id=call.message.chat.id)


@bot.message_handler(state=StartPollsessionStates.num_teams, is_digit=True)
def callback_create_pollsession_num_teams_text(message):
    '''
    | CREATE-POLLSESSION PIPELINE: STEP 1 (TEXT) |
    Revokes by: /create_pollsession's text
    Do: loads info from pressed markup button, reset state to StartPollsessionStates.num_players
    '''
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['num_teams'] = message.text

    bot.reply_to(message=message,
                 text=f'{message.text} teams were chosen. Now, choose number_players via inline keyboard or type manually.',
                 reply_markup=make_num_players_markup(message.text))

    bot.set_state(message.from_user.id, StartPollsessionStates.num_players, chat_id=message.chat.id)


def create_pollsession(teams_number, num_players):
    with app.app_context():
        max_players_per_team = int(num_players) / int(teams_number)

        logging.info(f'setup pollsession: {max_players_per_team, int(num_players), int(teams_number)}')

        pollsession = Pollsession(teams_number=teams_number,
                                  max_players_per_team=max_players_per_team)

        db.session.add(pollsession)
        db.session.commit()

        created_pollsession = Pollsession.fetch_active_pollsession()

        sended_msg = bot.send_message(config['GROUP_ID'], pollsession.render(), reply_markup=make_plus_minus_markup())

        bot.pin_chat_message(sended_msg.chat.id, sended_msg.message_id)

        pollsession.pinned_message_id = sended_msg.message_id
        dt = pollsession.creation_dt
        psid = pollsession.pollsession_id
        db.session.commit()

        return {'dt': dt, 'psid': psid}, sended_msg


@bot.callback_query_handler(func=None, state=StartPollsessionStates.num_players, config=num_players_factory.filter())
def callback_create_pollsession_num_players(call):
    with app.app_context():
        with bot.retrieve_data(call.from_user.id) as data:
            data['num_players'] = call.data.split(':')[1]
            num_players = data['num_players']
            teams_number = data['num_teams']

    created_pollsession, msg = create_pollsession(teams_number, num_players)
    dt, psid = created_pollsession['dt'], created_pollsession['psid']

    bot.reply_to(message=call.message,
                 text=f'Session with <b>id={psid}</b> created at {dt}\n')

@bot.message_handler(state=StartPollsessionStates.num_players, is_digit=True)
def callback_create_pollsession_num_players_text(message):
    with bot.retrieve_data(message.from_user.id) as data:
        teams_number = data['num_teams']
        num_players = message.text

    created_pollsession, msg = create_pollsession(teams_number, num_players)
    dt, psid = created_pollsession['dt'], created_pollsession['psid']

    with app.app_context():
        bot.reply_to(message=message,
                     text=f'Session with <b>id={psid}</b> created at {dt}\n')

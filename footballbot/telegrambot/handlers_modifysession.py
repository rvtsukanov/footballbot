import logging

from footballbot.extensions import bot
from footballbot.models.pollsession import Pollsession
from footballbot.telegrambot.states import StartPollsessionStates, ModifyPollsessionStates
from footballbot.telegrambot.callback_factories import num_players_factory, num_teams_factory, modify_players_factory
import telebot
from footballbot import app, db
from footballbot.telegrambot.markups import make_plus_minus_markup, make_num_players_markup, make_modify_players_markup

@bot.message_handler(commands=['modify_players_num'])
def modify_players_num(message):
    with app.app_context():
        if not Pollsession.check_if_active_exists():
            return bot.reply_to(message=message, text='Session not exists. Create it fist via /create_pollsession command')

        else:
            bot.reply_to(message=message,
                         text='Pick player amount modification',
                         reply_markup=make_modify_players_markup())
            bot.set_state(message.from_user.id, ModifyPollsessionStates.modify_players, chat_id=message.chat.id)

@bot.callback_query_handler(func=None, state=ModifyPollsessionStates.modify_players, config=modify_players_factory.filter())
def modify_players_num(call):
    answer = modify_players_factory.parse(call.data)
    answer_int = int(answer[answer['@']])
    logging.info(f'Got answer: {answer_int}')

    with app.app_context():
        pollsession = Pollsession.fetch_active_pollsession()
        if answer_int > 0:
            pollsession.increase_num_players_by_n(answer_int)
            db.session.commit()
        elif answer_int < 0:
            pollsession.decrease_num_players_by_n(answer_int) #TODO: return votes to be deleted
            db.session.commit()

    bot.reply_to(message=call.message,
                 text=('Decrease' if answer_int < 0 else 'Increase') + f' by {answer_int}')
@bot.message_handler(commands=['increase_players_num'])
def decrease_players_num(message):
    if Pollsession.check_if_active_exists():
        active_pollsession = Pollsession.fetch_active_pollsession()
        # active_pollsession


@bot.message_handler(commands=['decrease_teams_num'])
def decrease_teams_num(message):
    pass


@bot.message_handler(commands=['increase_teams_num'])
def increase_teams_num(message):
    pass
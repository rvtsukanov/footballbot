import logging

from footballbot.extensions import bot
from footballbot.telegrambot.states import StartPollsessionStates, ModifyPollsessionStates
from footballbot.telegrambot.callback_factories import plus_minus_factory
from footballbot.models.pollsession import Pollsession
from footballbot.models.player import Player
import telebot
from footballbot import app
from footballbot.telegrambot.markups import make_plus_minus_markup, make_num_players_markup
from footballbot.extensions import db

config = app.config

@bot.callback_query_handler(func=None, config=plus_minus_factory.filter())
def callback_query(call):
    player_id = call.from_user.id
    with app.app_context():
        pollsession = Pollsession.find_pollsession_by_message(call.message.id)
        player = Player.find_player(player_id=player_id)

        if not player:
            p = Player(player_id=call.from_user.id, telegram_name=call.from_user.name)
            db.session.add(p)
            db.session.commit()

        answer = plus_minus_factory.parse(call.data)

        logging.info(f'Answer: {answer}')

        if answer['plus_minus'] == "+":
            pollsession.add_player(player)
            db.session.commit()
            bot.edit_message_text(text=pollsession.render(), chat_id=config['GROUP_ID'],
                                  message_id=pollsession.pinned_message_id,
                                  reply_markup=make_plus_minus_markup())
        elif answer[answer['@']] == '-':
            pollsession.delete_player(player)
            db.session.commit()
            bot.edit_message_text(text=pollsession.render(), chat_id=config['GROUP_ID'],
                                  message_id=pollsession.pinned_message_id, reply_markup=make_plus_minus_markup())

        elif answer[answer['@']] == 'activate':
            player = Player.find_player(player_id=player_id)
            if player.get_role() == 'admin':
                pollsession.calculate_pollsession(config['GAME_COST'])
                bot.edit_message_text(text=pollsession.render(), chat_id=config['GROUP_ID'],
                                      message_id=pollsession.pinned_message_id, reply_markup=make_plus_minus_markup(activate=False))
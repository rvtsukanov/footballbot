from footballbot.extensions import bot
from footballbot.telegrambot.states import StartPollsessionStates, ModifyPollsessionStates
from footballbot.telegrambot.callback_factories import num_players_factory, num_teams_factory
import telebot
from footballbot import app
from footballbot.telegrambot.markups import make_plus_minus_markup, make_num_players_markup

config = app.config

from footballbot.models.pollsession import Pollsession
from footballbot.extensions import db

@bot.callback_query_handler(func=None, config=num_teams_factory.filter())
def callback_create_pollsession_num_teams(call):
    bot.reply_to(call.message, f'Here we go: {call.data}')

    with bot.retrieve_data(call.from_user.id) as data:
        data['num_teams'] = call.data.split(':')[1]
        num_players = data['num_teams']

    #     if data:
    #         if not data['num_teams']:
    #             data['num_teams'] = call.data
    #         else:
    #             bot.send_message(call.message.chat_id, 'Smth went wrong:( (Already have data via chat text form)')


    # rng_players_per_team_map = {2: [10, 12, 14, 16, 18, 20],
    #                             3: [12, 15, 18, 21],
    #                             4: [12, 16, 20]}
    #
    # markup = telebot.types.InlineKeyboardMarkup()
    # markup.row_width = 3
    # markup.add(*[telebot.types.InlineKeyboardButton(num,
    #                                                 callback_data=num_players_factory.new(num))
    #              for num in rng_players_per_team_map[int(num_players)]])

    bot.set_state(call.message.from_user.id, StartPollsessionStates.num_players)

    bot.reply_to(message=call.message,
                 text=f'{call.data} teams were chosen. Now, choose number_players via inline keyboard or type manually.',
                 reply_markup=make_num_players_markup(num_players))



def create_pollsession(teams_number, num_players):
    with app.app_context():
        max_players_per_team = int(num_players) / int(teams_number)

        pollsession = Pollsession(teams_number=teams_number,
                                  max_players_per_team=max_players_per_team)

        db.session.add(pollsession)
        db.session.commit()

        created_pollsession = Pollsession.fetch_active_pollsession()

        sended_msg = bot.send_message(config['GROUP_ID'], pollsession.render(), reply_markup=make_plus_minus_markup())

        bot.pin_chat_message(sended_msg.chat.id, sended_msg.message_id)

        pollsession.pinned_message_id = sended_msg.message_id
        db.session.commit()

        return created_pollsession, sended_msg


@bot.callback_query_handler(func=None, config=num_players_factory.filter())
def callback_create_pollsession_num_players(call):

    with app.app_context():
        with bot.retrieve_data(call.from_user.id) as data:
            data['num_players'] = call.data.split(':')[1]
            num_players = data['num_players']
            teams_number = data['num_teams']

    created_pollsession, msg = create_pollsession(num_players, teams_number)

    bot.reply_to(message=call.message,
                 text=f'Session with <b>id={created_pollsession.pollsession_id}</b> created at {created_pollsession.creation_dt}\n' +
                      f'Number of teams is {created_pollsession.teams_number}\nTotal number of players is {created_pollsession.max_players}')


@bot.message_handler(state=StartPollsessionStates.num_teams, is_digit=True)
def callback_create_pollsession_num_teams_text(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['num_teams'] = message.text

    bot.reply_to(message=message,
                 text=f'{message.text} teams were chosen. Now, choose number_players via inline keyboard or type manually.',
                 reply_markup=make_num_players_markup(message.text))

    bot.set_state(message.from_user.id, StartPollsessionStates.num_players, chat_id=message.chat.id)


@bot.message_handler(state=StartPollsessionStates.num_players, is_digit=True)
def callback_create_pollsession_num_players_text(message):
    with bot.retrieve_data(message.from_user.id) as data:
        teams_number = data['num_teams']
        data['num_players'] = message.text





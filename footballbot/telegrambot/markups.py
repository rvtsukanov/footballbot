import telebot
from footballbot.telegrambot.callback_factories import num_players_factory, plus_minus_factory, modify_players_factory

def make_num_players_markup(num_players: int):


    rng_players_per_team_map = {2: [10, 12, 14, 16, 18, 20],
                                3: [12, 15, 18, 21],
                                4: [12, 16, 20]}


    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(*[telebot.types.InlineKeyboardButton(num,
                                                    callback_data=num_players_factory.new(num))
                 for num in rng_players_per_team_map.get(int(num_players), [])])

    return markup


def make_plus_minus_markup(activate=True):
    markup = telebot.types.InlineKeyboardMarkup()
    # markup.row_width = 2

    if activate:
        markup.add(
            telebot.types.InlineKeyboardButton("➕", callback_data=plus_minus_factory.new('+')),
            telebot.types.InlineKeyboardButton("➖", callback_data=plus_minus_factory.new('-'))
        )
        markup.add(telebot.types.InlineKeyboardButton("Активировать", callback_data=plus_minus_factory.new('activate')))

    return markup


def make_modify_players_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(
        *[telebot.types.InlineKeyboardButton('+' + str(num), callback_data=modify_players_factory.new(str(num))) for num in [1, 2, 3, 4]]
    )
    markup.add(
        *[telebot.types.InlineKeyboardButton(num, callback_data=modify_players_factory.new(str(num))) for num in [-1, -2, -3, -4]]
    )
    return markup

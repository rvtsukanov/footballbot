import telebot
from footballbot.telegrambot.callback_factories import num_players_factory

def make_num_players_markup(num_players: int):


    rng_players_per_team_map = {2: [10, 12, 14, 16, 18, 20],
                                3: [12, 15, 18, 21],
                                4: [12, 16, 20]}


    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(*[telebot.types.InlineKeyboardButton(num,
                                                    callback_data=num_players_factory.new(num))
                 for num in rng_players_per_team_map.get(int(num_players), [])])


def make_plus_minus_markup(activate=True):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2

    if activate:
        markup.add(
            telebot.types.InlineKeyboardButton("➕", callback_data=f"+"),
            telebot.types.InlineKeyboardButton("➖", callback_data=f"-")
        )
        markup.add(telebot.types.InlineKeyboardButton("Активировать", callback_data=f"Calculate"))

    return markup
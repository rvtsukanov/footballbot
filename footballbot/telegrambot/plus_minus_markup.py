import telebot


def make_plus_minus_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        telebot.types.InlineKeyboardButton("+", callback_data=f"+"),
        telebot.types.InlineKeyboardButton("-", callback_data=f"-")
    )
    return markup

plus_minus_markup = make_plus_minus_markup()
import telebot


def plus_minus_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        telebot.types.InlineKeyboardButton("+", callback_data="+"),
        telebot.types.InlineKeyboardButton("-", callback_data="-"),
    )
    return markup
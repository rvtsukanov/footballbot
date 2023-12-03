import telebot


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

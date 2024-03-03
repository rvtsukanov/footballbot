from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot import types

from footballbot.extensions import bot

class ProductsCallbackFilter(AdvancedCustomFilter):
    key = 'config'
    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


num_teams_factory = CallbackData('num_teams', prefix='num_teams')
num_players_factory = CallbackData('num_players', prefix='num_players')

bot.add_custom_filter(ProductsCallbackFilter())
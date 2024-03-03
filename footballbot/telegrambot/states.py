from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup

class StartPollsessionStates(StatesGroup):
    num_teams = State()
    num_players = State()

class ModifyPollsessionStates(StatesGroup):
    pass


# from telebot.callback_data import CallbackData

#

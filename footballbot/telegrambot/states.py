from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup

class StartPollsessionStates(StatesGroup):
    num_teams = State()
    num_players = State()


class ModifyPollsessionStates(StatesGroup):
    modify_teams = State()
    modify_players = State()

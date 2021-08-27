import datetime
import logging
import yaml
import os

NUM_PLAYERS = yaml.safe_load(open('./config.yaml', 'r'))['num_players']
NUM_EXTRA_PLAYERS = yaml.safe_load(open('./config.yaml', 'r'))['num_extra_players']

def read_parameter(param_name):
    if os.getenv(param_name.upper()):
        return os.getenv(param_name.upper())
    else:
        return yaml.safe_load(open('./config.yaml', 'r'))[param_name]


class PollSession:
    def __init__(self,
                 session_start_time,
                 session_end_time,
                 is_closed=True,
                 game_date=None):

        self.session_start_time = session_start_time
        self.session_end_time = session_end_time

        self._create_time = datetime.datetime.now()
        self._is_closed = is_closed

        self.game_date = game_date # mb make a propery?

        self.player_set = {}
        self.extra_player_set = {}

    def __repr__(self):
        return f'{self.session_start_time}__{self.session_end_time} with {list(self.player_set)} players'

    def remove_player_from_session(self, player):
        if player in self.player_set:
            logging.info(f'Removing {player} from player-set')
            self.player_set.pop(player)
            if len(self.extra_player_set) > 0:
                self.player_set[list(self.extra_player_set)[0]] = None

        elif player in self.extra_player_set:
            logging.info(f'Removing {player} from extra player set')
            self.player_set.pop(player)


    def close_pollsession(self):
        self._is_closed = True

    def open_pollsession(self):
        self._is_closed = False


    def add_player_to_session(self, player):
        if len(self.player_set) < NUM_PLAYERS:
            logging.info(f'Adding {player} to main player set')
            self.player_set[player] = None

        elif (len(self.player_set) >= NUM_PLAYERS) and (len(self.player_set) <= NUM_EXTRA_PLAYERS):
            logging.info(f'Adding {player} to extra set')
            self.extra_player_set[player] = None

        else:
            logging.info(f'Queue is full.')


    def render_status(self):
        return f''' 
        *Session starts at: {self.session_start_time.date()} for game: {self.game_date}*
        ''' + ' - '.join(['@' + player for player in list(self.player_set)]) + '\n\n' + ' * '.join(['@' + player for
                                                                                                    player in list(
                self.extra_player_set)])









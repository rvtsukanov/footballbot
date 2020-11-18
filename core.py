import datetime
import logging

class Player:
    def __init__(self, id,
                 username,
                 name=None,
                 surname=None,
                 agreed=False,
                 is_admin=False,
                 ):

        self.id = id
        self.username = username
        self.name = name
        self.surname = surname
        self.agreed = agreed
        self.is_admin = is_admin


    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f'{(self.name is not None) * self.name} {(self.surname is not None) * self.surname} ({self.id}) agree status: {self.agreed}'


class Location:
    def __init__(self, lat, lon, name):
        pass
        # 55.718779, 37.551103



class PollSession:
    def __init__(self,
                 active_time_start,
                 active_time_end,
                 is_closed=True,
                 location=None):

        self.active_time_start = active_time_start
        self.active_time_end = active_time_end

        self._create_time = datetime.datetime.now()
        self._is_closed = is_closed

        self.player_set = {}

    def remove_player_from_session(self, player):
        if player in self.player_set:
            logging.info(f'Removing {player} from player-set')
            self.player_set.pop(player)


    def close_pollsession(self):
        self._is_closed = True

    def open_pollsession(self):
        self._is_closed = False


    def add_player_to_session(self, player):
        self.remove_player_from_session(player)
        logging.info(f'Adding {player} to player-set')
        self.player_set.add(player)








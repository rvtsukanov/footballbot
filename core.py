import datetime
import logging


class Player:
    def __init__(self, id,
                 username,
                 first_name=None,
                 last_name=None,
                 agreed=False,
                 is_admin=False,
                 is_bot=False,
                 language_code='ru'
                 ):

        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.agreed = agreed
        self.is_admin = is_admin
        self.is_bot = is_bot
        self.language_code = language_code


    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f'{(self.username is not None) * self.username} ({self.id}) status:{self.agreed}'


class Message:
    def __init__(self, message_id: int,
                 message_from: Player,
                 chat: str,
                 date: int,
                 text: str):
        self.message_id = message_id
        self.message_from = message_from
        self.chat = chat
        self.date = date
        self.text = text


    def __hash__(self):
        return hash(self.message_id)


    def __eq__(self, other):
        return self.message_id == other.message_id

    @property
    def hdate(self):
        return datetime.datetime.fromtimestamp(self.date)

    def __repr__(self):
        return f'| <{self.message_id}> @{self.message_from} text:{self.text} |'


class Keyboard:
    def __init__(self, inline=False, buttons=[], **kwargs):
        self.kb_markup = {inline * 'keyboard' + (not inline) * 'inline_keyboard': [{'text': text} for text in buttons],
                     **kwargs}

    def serialize(self):
        #TODO: implement
        pass


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

        self.player_set = set()

    def __repr__(self):
        return f'{self.active_time_start}__{self.active_time_end} with {self.player_set} players'

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








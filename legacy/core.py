class Game:
    def __init__(self, date):
        self.date = date


class Player:
    def __init__(self, username, priority=1):
        self.username = username
        self.priority = priority
        self.creation_timestamp = datetime.datetime.now()


class PollSession:
    def __init__(self,
                 session_start_time,
                 session_end_time,
                 session_id,
                 conn,
                 is_closed=True,
                 game_date=None,
                 teams_number=2,
                 players_per_team=9,
                 extra_players_per_team=1):

        self.session_start_time = session_start_time
        self.session_end_time = session_end_time

        self.conn = conn

        self.session_id = session_id

        self._create_time = datetime.datetime.now()
        self._is_closed = is_closed

        self.game_date = game_date

        self.teams_number = teams_number
        self.players_per_team = players_per_team

        self.player_set = queue.PriorityQueue(pmaxsize=players_per_team)
        self.extra_player_set = queue.PriorityQueue(maxsize=extra_players_per_team)


    def __repr__(self):
        return f'{self.session_start_time}__{self.session_end_time} with {list(self.player_set)} players'


    @property
    def is_full(self):
        return sum(self.player_set.values()) == constants.NUM_PLAYERS

    def remove_player_from_session(self, player):
        if player in self.player_set:
            logging.info(f'Removing {player} from player-set')
            if self.player_set[player] > 1:
                self.player_set[player] -= 1

            else:
                self.player_set.pop(player)

            # if len(self.extra_player_set) > 0:
            #     self.player_set[] = None

        elif player in self.extra_player_set:
            logging.info(f'Removing {player} from extra player set')
            self.player_set.pop(player)

    def close_pollsession(self):
        self._is_closed = True

    def open_pollsession(self):
        self._is_closed = False


    def _add_player_to_session_db(self, player, extra=False):
        pass


    def add_player_to_session(self, player):

        try:
            self.player_set.put(player)
            self._add_player_to_session_db(player)

        except queue.Full:
            logging.error('Main player-set is full. Trying to use extra-one')
            try:
                self.extra_player_set.put(player)
                self._add_player_to_session_db(player, extra=True)

            except queue.Full:
                logging.error('Extra player-set is full. Addition is incomplete')


        # if sum(self.player_set.values()) < NUM_PLAYERS:
        #     logging.info(f'Adding {player} to main player set')
        #     self.player_set[player] += 1
        #
        # elif (len(self.player_set) >= NUM_PLAYERS) and (len(self.player_set) <= NUM_EXTRA_PLAYERS):
        #     logging.info(f'Adding {player} to extra set')
        #     self.extra_player_set[player] += 1
        #
        # else:
        #     logging.info(f'Queue is full.')


    def render_status(self):

        emoji_status = u'\U000027a1' if not self.is_full else u'\U0000274c'
        print('FULL?: ', self.is_full)

        header = emoji_status + f'* Session starts at: {self.session_start_time.date()} for game: {self.game_date}* \n\n'

        rows = [header]

        for n, user_id in enumerate(self.player_set):
            print(f'USER ID : {user_id}')
            # user_id = user_id.replace("_", "\_")
            row = f'{n + 1}. @{user_id}' if self.player_set[user_id] == 1 else f'{n + 1}. @{user_id}' + f' (+{self.player_set[user_id] - 1})'
            row = row.replace("_", "\_") # in order to proceed with markup
            rows.append(row)

        print(self.player_set)
        print('SOME USEFUL: ' + '\n'.join(rows))

        return '\n'.join(rows)


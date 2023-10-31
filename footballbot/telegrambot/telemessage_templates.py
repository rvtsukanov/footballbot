CURRENT_POLLSESSION = '''
    emoji_status = u'\U000027a1' if not self.is_full else u'\U0000274c'
    print('FULL?: ', self.is_full)

    header = emoji_status + f'* Session starts at: {self.session_start_time.date()} for game: {self.game_date}* \n\n'

    rows = [header]

    for n, user_id in enumerate(self.player_set):
        print(f'USER ID : {user_id}')
        # user_id = user_id.replace("_", "\_")
        row = f'{n + 1}. @{user_id}' if self.player_set[
                                            user_id] == 1 else f'{n + 1}. @{user_id}' + f' (+{self.player_set[user_id] - 1})'
        row = row.replace("_", "\_")  # in order to proceed with markup
        rows.append(row)

    print(self.player_set)
    print('SOME USEFUL: ' + '\n'.join(rows))

    return '\n'.join(rows)
    '''
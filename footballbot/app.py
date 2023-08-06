

# app = Flask(__name__)


# with app.app_context():
#     db.create_all()




# TODO: make possible to create auto-closing pollsessions
# @app.route('/fetch_active_pollsession')
# def fetch_active_pollsession():
#     pass
# def


# remove
# oldpost = jack.posts.filter(Post.headline == "old post").one()
# jack.posts.remove(oldpost)
#
# jack.posts.append(Post("new post"))


# with app.app_context():

    # db.drop_all()
    # db.create_all()
    # db.session.add(Pollsessions(teams_number=2,
    #                             max_players_per_team=18,
    #                             pinned_message_id=0))

    # db.session.add(Players(player_id=100501,
    #                        telegram_name='drakosha2'))

    # current_pollsession = Pollsession()
    # new_player1 = Player(player_id=100, telegram_name='pupkin')
    # new_player2 = Player(player_id=101, telegram_name='zalupkin')
    # #
    # current_pollsession.players.append(new_player1)
    # current_pollsession.players.append(new_player1)
    #
    # current_pollsession.players.append(new_player2)
    # current_pollsession.players.append(new_player2)
    # #
    # db.session.add(current_pollsession)

    # last condition
    # active_pollsession = db.session.query(Pollsession).order_by(Pollsession.pollsession_id.desc()).first()
    # active_pollsession.players.append(new_player2)
    # active_pollsession.players.append(new_player2)

    # player = Player.query.filter_by(telegram_name='pupkin').one()
    # print(player.telegram_name)
    # print(player.player_id)
    #
    # print(active_pollsession)
    # print(active_pollsession.players)

    # active_pollsession.players.append(player)


    # db.session.commit()


# 2 проблемы:
#  1 херня с добавлением строчки через релейшоншипы
#  2 херня с уникальностью значений при селекте







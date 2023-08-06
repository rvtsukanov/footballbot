from footballbot.extensions import db
import datetime

pollsession2player = db.Table('pollsession2player',
                              db.Column('row_id', db.Integer, autoincrement=True, primary_key=True, nullable=False),
                              db.Column('pollsession_id', db.Integer, db.ForeignKey('pollsession.pollsession_id')),
                              db.Column('player_id', db.Integer, db.ForeignKey('player.player_id')),
                              db.Column('insert_dt', db.DateTime, default=datetime.datetime.utcnow))
from footballbot.extensions import db
import json

class Pollsession(db.Model):
    pollsession_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    teams_number = db.Column(db.Integer)
    max_players_per_team = db.Column(db.Integer)
    pinned_message_id = db.Column(db.Integer)
    players = db.relationship('Player', secondary='pollsession2player', backref='pollsession')

    def __repr__(self):
        return f'PS[{self.pollsession_id}][{self.players}]'

    @classmethod
    def fetch_last_pollsession(cls):
        return db.session.query(cls).order_by(cls.pollsession_id.desc()).first()

    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


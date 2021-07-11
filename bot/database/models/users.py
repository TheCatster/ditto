from bot.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BIGINT, primary_key=True)
    level = db.Column(db.Integer, default=0)
    xp = db.Column(db.BIGINT, default=0)
    times_hosted = db.Column(db.BIGINT, default=0)

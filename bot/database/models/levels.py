from bot.database import db


class Level(db.Model):
    __tablename__ = "levels"

    set_level = db.Column(db.BIGINT, primary_key=True)
    set_xp = db.Column(db.BIGINT)

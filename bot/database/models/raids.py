from bot.database import db


class Raid(db.Model):
    __tablename__ = "raids"

    id = db.Column(db.BIGINT, primary_key=True)
    guild_id = db.Column(db.BIGINT, db.ForeignKey("guilds.id"))
    pokemon = db.Column(db.Text)
    shiny = db.Column(db.Boolean)
    gmax = db.Column(db.Boolean)
    host_id = db.Column(db.BIGINT)

from bot.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BIGINT, primary_key=True)
    report_count = db.Column(db.Integer, default=0)
    host_banned = db.Column(db.Boolean, default=False)
    reports_created_count = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=0)
    xp = db.Column(db.BIGINT, default=0)
    times_hosted = db.Column(db.BIGINT, default=0)

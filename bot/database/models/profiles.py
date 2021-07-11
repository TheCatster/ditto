from bot.database import db


class Profile(db.Model):
    __tablename__ = "profiles"

    user_id = db.Column(db.BIGINT, primary_key=True)
    friend_code = db.Column(db.Text, default="Not Set")
    user_name = db.Column(db.Text, default="Not Set")
    timezone = db.Column(db.Text)

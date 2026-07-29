from app.database import db
from datetime import datetime


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    key = db.Column(
        db.String(50),
        nullable=False
    )
    value = db.Column(
        db.String(50),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

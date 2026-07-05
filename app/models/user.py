from typing import List

from app.database.db import db
from datetime import datetime, timezone

from app.models.query import Query


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    date_joined = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def get_user_by_id(user_id):
        return User.query.filter_by(user_id=user_id).one_or_none()

    def get_user_queries(self) -> List[Query]:
        return Query.query.filter_by(user_id=self.user_id).all()
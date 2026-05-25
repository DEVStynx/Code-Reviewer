from datetime import datetime
from app.database.db import db


class Query(db.Model):
    __tablename__ = "queries"

    query_id = db.Column(db.Integer, primary_key=True)

    query_creation = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref="queries"
    )

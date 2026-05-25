from app.database.db import db
from app.models.user import User
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()


def check_username_valid(username: str) -> bool:
    return ' ' not in username


def check_username_available(username: str) -> bool:
    count = User.query.filter_by(username=username).count()
    return count == 0


def hash_password(password: str) -> str:
    return ph.hash(password)


def check_password_matching(db_hash, password) -> bool:
    try:
        return ph.verify(db_hash, password)
    except VerifyMismatchError:
        return False


def check_matching_user_password(username: str, password: str) -> bool:
    if check_username_available(username):
        return False

    user_object = User.query.filter_by(username=username).scalar()
    return check_password_matching(user_object.password_hash, password)


def add_user_db(username: str, password: str) -> bool:
    if not check_username_available(username):
        return False
    if not check_username_valid(username):
        return False

    user_object = User()
    user_object.username = username
    user_object.password_hash = hash_password(password)
    db.session.add(user_object)
    db.session.commit()

    return True


def remove_user_db(username: str) -> bool:
    if check_username_available(username):
        return False

    User.query.filter_by(username=username).delete()
    db.session.commit()

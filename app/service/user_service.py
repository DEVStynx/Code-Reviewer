from app.database.db import db
from app.models.user import User
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import flash, redirect
from enum import Enum
from flask_jwt_extended import create_access_token, set_access_cookies

ph = PasswordHasher()


def check_username_valid(username: str) -> bool:
    return ' ' not in username and not len(username) < 3


def check_password_valid(password: str) -> bool:
    return " " not in password and not len(password) < 3


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

    user_object = User.query.filter_by(username=username).one_or_none()
    return check_password_matching(user_object.password_hash, password)


class RegistrationStatus(Enum):
    SUCCESS = 0
    ALREADY_EXISTS = 1
    INVALID_USERNAME = 2
    INVALID_PASSWORD = 3


def add_user_db(username: str, password: str) -> RegistrationStatus:
    if not check_username_available(username):
        return RegistrationStatus.ALREADY_EXISTS
    if not check_username_valid(username):
        return RegistrationStatus.INVALID_USERNAME
    if not check_password_valid(password):
        return RegistrationStatus.INVALID_PASSWORD

    user_object = User()
    user_object.username = username
    user_object.password_hash = hash_password(password)
    db.session.add(user_object)
    db.session.commit()

    return RegistrationStatus.SUCCESS


def remove_user_db(username: str) -> bool:
    if check_username_available(username):
        return False

    User.query.filter_by(username=username).delete()
    db.session.commit()
    return True


def create_user_token(user: User) -> str:
    access_token = create_access_token(identity=str(user.user_id))
    return access_token


def register_user(username: str, password: str):
    match add_user_db(username, password):
        case RegistrationStatus.SUCCESS:
            print(f"registered User: {username} with pw: {password}")
            user = User.query.filter_by(username=username).one_or_none()
            response = redirect("/")
            set_access_cookies(response, create_user_token(user))
            return response
        case RegistrationStatus.INVALID_USERNAME:
            flash("Invalid Username", "danger")
            return redirect("/register")
        case RegistrationStatus.ALREADY_EXISTS:
            flash("User already exists", "danger")
            return redirect("/register")
        case RegistrationStatus.INVALID_PASSWORD:
            flash("Invalid Password", "danger")
            return redirect("/register")


def login_user(username: str, password: str):
    user = User.query.filter_by(username=username).one_or_none()

    if not user or not check_password_matching(user.password_hash, password):
        flash("Invalid Username or Password", "danger")
        return redirect("/login")

    access_token = create_user_token(user)
    response = redirect("/")
    set_access_cookies(response, access_token)
    return response


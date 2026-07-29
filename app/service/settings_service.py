from datetime import datetime
from typing import List

from flask import redirect, render_template, make_response
from flask_jwt_extended import get_current_user
from app.database import db

from app.models.user import User
from app.models.user_settings import UserSettings

ALLOWED_SETTINGS = ["theme", "prompt-check"]


def get_user_settings():
    current_user = get_current_user()
    if not current_user:
        return redirect("/login")

    settings: List[UserSettings]
    settings = current_user.get_user_settings()
    setting_values = {setting.key: setting.value for setting in settings}
    return render_template("settings.html", settings=settings, setting_values=setting_values)


def set_user_setting(key: str, value: str):
    current_user = get_current_user()
    if not current_user:
        r = make_response()
        r.status_code = 400
        r.data = "{'msg':'unallowed user'}"
        return r

    if key not in ALLOWED_SETTINGS:
        print(f"provided key: {key}, ")
        r = make_response()
        r.status_code = 404
        r.data = "{'msg':'unallowed setting'}"
        return r

    settings: List[UserSettings] = current_user.get_user_settings()
    for setting in settings:
        if setting.key == key:
            setting.value = value
            setting.updated_at = datetime.utcnow()
            db.session.commit()

            r = make_response()
            r.status_code = 200
            return r

    settings_obj = UserSettings()
    settings_obj.user_id = current_user.user_id
    settings_obj.key = key
    settings_obj.value = value
    db.session.add(settings_obj)
    db.session.commit()

    r = make_response()
    r.status_code = 200
    return r


def get_user_setting(user: User, key: str) -> str | None:
    settings = user.get_user_settings()
    for setting in settings:
        if setting.key == key.lower():
            return setting.value
    return None

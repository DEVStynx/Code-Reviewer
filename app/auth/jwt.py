from flask_jwt_extended import JWTManager
from app.models.user import User
from app.database.db import db

jwt = JWTManager()




@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    user_id = jwt_data["sub"]
    return User.query.get(user_id)
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.service.ai_service import setupOpenAIAPI
from app.database.db import db
from app.auth.jwt import jwt

migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    jwt.init_app(app)
    db.init_app(app)

    setupOpenAIAPI(app)

    from .api.routes import index_bp, api_bp
    app.register_blueprint(index_bp)
    app.register_blueprint(api_bp)

    migrate.init_app(app, db)

    from app import models
    return app

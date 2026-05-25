from flask import Flask
from app.service.ai_service import setupOpenAIAPI
from app.database.db import db
from flask_migrate import Migrate

migrate = Migrate()
def create_app():
    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    setupOpenAIAPI(app)

    from .api.routes import index_bp, api_bp
    app.register_blueprint(index_bp)
    app.register_blueprint(api_bp)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models
    return app

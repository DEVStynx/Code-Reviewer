from flask import Flask

def create_app():
    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    from .api.routes import index_bp, api_bp
    app.register_blueprint(index_bp)
    app.register_blueprint(api_bp)

    return app
from flask import Flask

def create_app():
    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    from .api.routes import index_bp
    app.register_blueprint(index_bp)

    return app
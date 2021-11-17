from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import env_config


db = SQLAlchemy()


def create_app(config_key=None):
    app = Flask(__name__)
    config_obj_key = config_key if config_key in env_config else app.config["ENV"]
    app.config.from_object(env_config[config_obj_key])

    initialize_extensions(app)
    initialize_app_modules(app)

    return app


def initialize_extensions(app):
    db.init_app(app)


def initialize_app_modules(app):
    with app.app_context():
        from . import views
        from . import auth
        from . import commands
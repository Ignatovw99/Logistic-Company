from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import env_config


db = SQLAlchemy()
csrf = CSRFProtect()


def create_app(config_key=None):
    app = Flask(__name__)
    config_obj_key = config_key if config_key in env_config else app.config["ENV"]
    app.config.from_object(env_config[config_obj_key])

    initialize_extensions(app)
    initialize_app_modules(app)

    return app


def initialize_extensions(app):
    # initialize each Flask extension here to be activated in the app context
    db.init_app(app)
    csrf.init_app(app)


def initialize_app_modules(app):
    with app.app_context():
        from app.auth.views import auth
        from app.main.views import main
        from app.common.commands import commands
        from app.office.views import office
        from app.employee.views import employee
        from app.shipment.views import shipment

        app.register_blueprint(auth)
        app.register_blueprint(main)
        app.register_blueprint(commands)
        app.register_blueprint(office, url_prefix="/offices")
        app.register_blueprint(employee, url_prefix="/employees")
        app.register_blueprint(shipment, url_prefix="/shipments")
        
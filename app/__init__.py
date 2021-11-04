from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import env_config


app = Flask(__name__)
app.config.from_object(env_config[app.config["ENV"]])
db = SQLAlchemy(app)


from app import views
from app import models
from app import commands
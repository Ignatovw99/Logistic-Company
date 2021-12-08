
from flask import Flask, render_template, flash, redirect, request, url_for
from flask.json import jsonify
from app.models import User
from validator_reg import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from config import env_config

db = SQLAlchemy()

def create_app(config_key=None):
    app = Flask(__name__)
    config_obj_key = config_key if config_key in env_config else app.config["ENV"]
    app.config.from_object(env_config[config_obj_key])

    initialize_extensions(app)
    initialize_app_modules(app)
    app.config['SECRET_KEY'] = '0eb70a4c38502c60943698c824c98b20'

    app.static_folder = 'static'

    @app.route("/index")
    def index():
        return render_template("index.html")


    @app.route("/register", methods = ['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            firstname = form.firstname.data
            lastname = form.lastname.data
            address = form.address.data
            phone = form.phone.data
            password = form.password.data

            user_object = User.query.filter_by(username=username).first()
            if user_object:
                return "Someone else has taken that username."

            user = User(username=username, email = email, firstname = firstname, lastname = lastname, address = address, phone = phone, password = password)
            db.session.add(user)
            db.session.commit()
            return "Inserted into DB!"

        return render_template('signup.html', title = 'Register', form = form)

    @app.route("/login", methods = ['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            if form.username.data == 'adminblog' and form.password.data == 'password':
                return jsonify(request.form)
            else:
                return 'Login unsuccessful'
        return render_template('login.html', title = 'Login', form = form)



    if __name__ == "__main__":
        app.run(debug=True)    
    return app



def initialize_extensions(app):
    db.init_app(app)


def initialize_app_modules(app):
    with app.app_context():
        from . import views
        from . import auth
        from . import commands




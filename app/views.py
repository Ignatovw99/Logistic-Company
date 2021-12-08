from flask import current_app as app, render_template
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import env_config
from flask import Flask, render_template
from app.validator_reg import RegistrationForm, LoginForm
from app.models import User


db = SQLAlchemy()


@app.route("/")
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
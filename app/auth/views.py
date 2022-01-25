from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, Response
from app import db
from app.auth.util import current_user, role_required
from app.models import User, Role, Office, ShippingStatus, Shipment, ShippingAddress, Employee
from app.auth.forms import RegistrationForm, LoginForm

auth = Blueprint("auth", __name__)

@auth.route("/register", methods = ['GET', 'POST'])
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
        # return redirect(url_for("auth.login"))

    return render_template('auth/signup.html', title = 'Register', form = form)


@auth.route("/login", methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'adminblog' and form.password.data == 'password':
            return jsonify(request.form)
        else:
            return 'Login unsuccessful'
    return render_template('auth/login.html', title = 'Login', form = form)



@auth.app_context_processor
def inject_current_user():
    """
    Inject the current logged-in user as a variable into the context of the application templates
    """
    return dict(current_user=current_user)


@auth.app_context_processor
def inject_roles():
    """
    Inject all available roles as a variable into the context of the application templates
    """
    return dict(Role=Role)
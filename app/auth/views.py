from flask import Blueprint, render_template, flash, redirect, url_for

from app.models import User, Role

from app.auth.util import login_user, anonymous_required, add_remember_cookies, current_user
from app.auth.forms import RegistrationForm, LoginForm
from app.common.util import find_user_by_email

from app.common.util import persist_model


auth = Blueprint("auth", __name__)


@auth.route("/register", methods = ['GET', 'POST'])
@anonymous_required
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data       
        first_name = form.first_name.data
        last_name = form.last_name.data
        address = form.address.data
        phone_number = form.phone_number.data
        password = form.password.data

        if find_user_by_email(email):
            flash("This email is already taken")
        else:
            user = User(email = email, first_name = first_name, last_name = last_name, address = address, phone_number = phone_number, password = password)
            user.add_role(Role.CLIENT)
            persist_model(user)
            flash("Sucessful registration")
            return redirect(url_for("auth.login"))

    return render_template('auth/signup.html', title = 'Register', form = form)


@auth.route("/login", methods = ['GET', 'POST'])
@anonymous_required
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember_me = form.remember.data

        user = find_user_by_email(email)

        if user and user.verify_password(password):
            login_user(user)
            response = redirect(url_for("main.profile"))
            if remember_me:
                add_remember_cookies(response, user)
            flash("Logged in successfully")
            return response
        else:
            flash("Invalid credentials")

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

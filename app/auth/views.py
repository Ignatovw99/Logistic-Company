from flask import Blueprint, render_template, flash, redirect, request, url_for, current_app

from app.models import User, Role

from app.auth.util import delete_remember_cookies, login_required, login_user, anonymous_required, add_remember_cookies, current_user, logout_user
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
            flash("This email is already taken", "danger")
        else:
            user = User(email = email, first_name = first_name, last_name = last_name, address = address, phone_number = phone_number, password = password)
            user.add_role(Role.CUSTOMER)
            persist_model(user)
            flash("Sucessful registration", "success")
            return redirect(url_for("auth.login"))

    return render_template('auth/signup.html', form = form)


@auth.route("/login", methods = ['GET', 'POST'])
@anonymous_required
def login():
    form = LoginForm()

    if request.method == "GET" and current_app.config["REDIRECT_QUERY_PARAM"] in request.args:
        form.redirect.data = request.args[current_app.config["REDIRECT_QUERY_PARAM"]]

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember_me = form.remember.data
        redirect_data = form.redirect.data

        user = find_user_by_email(email)

        if user and user.verify_password(password):
            login_user(user)
            
            redirect_handler = redirect_data if redirect_data else "shipment.show"
            response = redirect(url_for(redirect_handler))
            
            if remember_me:
                add_remember_cookies(response, user)
            flash("Logged in successfully", "success")
            return response
        else:
            flash("Invalid credentials", "danger")

    return render_template('auth/login.html', form = form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    response = redirect(url_for("main.index"))
    delete_remember_cookies(response)
    flash("Logged out successfully", "success")
    return response


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

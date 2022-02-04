from flask import session, g, request, current_app, flash, redirect, url_for
from werkzeug.local import LocalProxy
from app import db
from app.models import Role, User, Remember
from itsdangerous.url_safe import URLSafeSerializer
from functools import wraps


current_user = LocalProxy(lambda: load_user())


def login_user(user):
    session["user_id"] = user.id


def logout_user():
    user_id = session.pop("user_id")
    Remember.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    g._current_user = False


def load_user():
    """
    This function gets the current logged in user from the session request.
    It stores the current user into the global application context for the given request (g). 
    It uses the Memoization technique, which optimizes the function execution.
    """
    _current_user = getattr(g, "_current_user", None)

    if _current_user is None:
        user = None
        if session.get("user_id"):
            user = User.query.get(session.get("user_id"))
        elif request.cookies.get("user_id"):
            user = User.query.get(
                int(decrypt_cookie(request.cookies.get("user_id")))
            )
            if user and user.check_remember_token(decrypt_cookie(request.cookies.get("remember_token"))):
                login_user(user)
        
        _current_user = g._current_user = user
        
    if not _current_user:
        # Create an anonymous user
        _current_user = User()

    return _current_user


def encrypt_cookie(cookie_content):
    serializer = URLSafeSerializer(current_app.config["SECRET_KEY"], salt="cookie")
    encrypted_cookie_content = serializer.dumps(cookie_content)
    return encrypted_cookie_content


def decrypt_cookie(encrypted_cookie_content):
    serializer = URLSafeSerializer(current_app.config["SECRET_KEY"], salt="cookie")
    try:
        cookie_content = serializer.loads(encrypted_cookie_content)
    except :
        cookie_content = -1
    return cookie_content


def add_remember_cookies(response, user):
    remember_token = user.create_remember_token()
    response.set_cookie("remember_token", encrypt_cookie(remember_token), max_age=60*60*24*100)
    response.set_cookie("user_id", encrypt_cookie(user.id), max_age=60*60*24*100)


def delete_remember_cookies(response):
    response.set_cookie("remember_token", "", max_age=0)
    response.set_cookie("user_id", "", max_age=0)


def login_required(view_func):
    @wraps(view_func)
    def handle_login_requirement(*args, **kwargs):
        if current_user.is_anonymous():
            flash("You need to be logged in", "danger")
            return redirect(url_for("auth.login", redirect_handler=request.blueprint + "." + view_func.__name__))
        return view_func(*args, **kwargs)

    return handle_login_requirement


def anonymous_required(view_func):
    @wraps(view_func)
    def handle_anonymous_requirement(*args, **kwargs):
        if current_user.is_authenticated():
            flash("You are already logged in", "warning")
            return redirect(url_for("shipment.show"))
        return view_func(*args, **kwargs)

    return handle_anonymous_requirement


def role_required(role):
    def role_required_wrapper(view_func):
        @wraps(view_func)
        def hanlde_role_requirement(*args, **kwargs):
            if not current_user.has_role(role):
                flash("You are not authorized to access this page", "danger")
                return redirect(url_for("shipment.show"))
            return view_func(*args, **kwargs)
        return hanlde_role_requirement
        
    return role_required_wrapper

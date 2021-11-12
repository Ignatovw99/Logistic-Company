from flask import session, g
from werkzeug.local import LocalProxy
from app import app
from app.models import User


current_user = LocalProxy(lambda: load_user())


def login_user(user):
    session["user_id"] = user.id


def logout_user():
    session.pop("user_id")


def load_user():
    """
    This function gets the current logged in user from the session request.
    It stores the current user into the global application context for the given request (g). 
    It uses the Memoization technique, which optimizes the function execution.
    """
    _current_user = getattr(g, "_current_user", None)

    if _current_user is None and session.get("user_id"):
        user = User.query.get(session.get("user_id"))
        if user:
            _current_user = g._current_user = user
            
    if _current_user is None:
        # Create an anonymous user
        _current_user = User()

    return _current_user


@app.context_processor
def inject_current_user():
    """
    Inject the current logged-in user as a variable into the context of the application templates
    """
    return dict(current_user=current_user)

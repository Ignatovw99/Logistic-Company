from app.models import User

def find_user_by_email(email):
    return User.query.filter_by(email=email).first()
    
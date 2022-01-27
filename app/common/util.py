from app import db
from app.models import User


def persist(object):
    db.session.add(object)
    db.session.commit()


def delete(object):
    db.session.delete(object)
    db.session.commit()


def find_user_by_email(email):
    return User.query.filter_by(email=email).first()
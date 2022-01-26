from app import db

def persist(object):
    db.session.add(object)
    db.session.commit()
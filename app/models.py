from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(200))
    telephone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(60), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User(first_name={self.first_name}, last_name={self.last_name})"

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


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    office_id = db.Column(db.Integer, db.ForeignKey("offices.id"))
    user = db.relationship(User, foreign_keys=id, lazy="joined")

    def __repr__(self):
        return f"Employee(first_name={self.user.first_name}, last_name={self.user.last_name}, office_id={self.office_id})"


class Office(db.Model):
    __tablename__ = "offices"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    address = db.Column(db.String(200), nullable=False)
    employees = db.relationship(Employee, backref="office", lazy="select")

    def __repr__(self):
        return f"Office(name={self.name}, address={self.address})"

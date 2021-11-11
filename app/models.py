from app import db
from werkzeug.security import generate_password_hash, check_password_hash

import enum


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(60), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)


    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)


    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


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


class ShippingStatus(enum.Enum):
    SHIPPED = 1
    DELIVERED = 2


class ShippingAddress(db.Model):
    __tablename__ = "shipping_addresses"

    id = db.Column(db.Integer, primary_key=True)
    office_id = db.Column(db.Integer, db.ForeignKey("offices.id"))
    address = db.Column(db.String(200))

    office = db.relationship(Office, foreign_keys=office_id, lazy="joined")
    
    def __repr__(self):
        return f"ShippingAddress(office_id={self.office_id}, address={self.address})"


class Shipment(db.Model):
    __tablename__ = "shipments"

    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(ShippingStatus), nullable=False, default=ShippingStatus.SHIPPED)
    from_address_id = db.Column(db.Integer, db.ForeignKey("shipping_addresses.id"), nullable=False, unique=True)
    to_address_id = db.Column(db.Integer, db.ForeignKey("shipping_addresses.id"), nullable=False, unique=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    acceptor_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    deliverer_id = db.Column(db.Integer, db.ForeignKey("employees.id"))

    from_address = db.relationship(ShippingAddress, foreign_keys=from_address_id, uselist=False, lazy="select")
    to_address = db.relationship(ShippingAddress, foreign_keys=to_address_id, uselist=False, lazy="select")
    sender = db.relationship(User, foreign_keys=sender_id, lazy="select")
    receiver = db.relationship(User, foreign_keys=receiver_id, lazy="select")
    acceptor = db.relationship(Employee, foreign_keys=acceptor_id, lazy="select")
    deliverer = db.relationship(Employee, foreign_keys=deliverer_id, lazy="select")

    def __repr__(self):
        return f"Shipment(weight={self.weight}, status={self.status})"
        
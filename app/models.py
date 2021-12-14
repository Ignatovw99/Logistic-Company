from app import db
from secrets import token_urlsafe 
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
    
    remember_hashes = db.relationship("Remember", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    roles = db.relationship("UserRole", backref="user", lazy="joined", cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return not "" == self.email and not self.email is None

    def is_anonymous(self):
        return not self.is_authenticated()

    def has_role(self, role):
        user_roles = [user_role.role for user_role in self.roles]
        return role in user_roles

    def create_remember_token(self):
        remember = Remember(self.id)
        db.session.add(remember)
        db.session.commit()
        return remember.token

    def check_remember_token(self, token):
        if token:
            for remember_hash in self.remember_hashes:
                if remember_hash.check_token(token):
                    return True
        return False

    def __repr__(self):
        return f"User(first_name={self.first_name}, last_name={self.last_name})"


class Role(enum.Enum):
    SYSTEM_ADMIN = 1
    CLIENT = 2
    EMPLOYEE = 3


class UserRole(db.Model):
    __tablename__ = "users_roles"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True, autoincrement=False)
    role = db.Column(db.Enum(Role), primary_key=True, autoincrement=False)
    
    def __repr__(self):
        return f"UserRole(user={self.user}, role={self.role})"


class Remember(db.Model):
    __tablename__ = "remembers"

    id = db.Column(db.Integer, primary_key=True)
    remember_hash = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, user_id):
        self.generate_token_hash()
        self.user_id = user_id
        
    def generate_token_hash(self):
        # This token is a temporary property. It will only exist until the instance of the Remember model gets deleted
        self.token = token_urlsafe(20)
        self.remember_hash = generate_password_hash(self.token)

    def check_token(self, token):
        return check_password_hash(self.remember_hash, token)

    def __repr__(self):
        return f"Remember(user={self.user}, remember_hash={self.remember_hash})"


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
        
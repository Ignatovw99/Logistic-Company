from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp

from app.models import Role

class EmployeeForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=20)])
    phone_number = StringField('Phone number', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators = [DataRequired(), Regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$", message="Password should be eight characters, at least one uppercase letter, one lowercase letter and one number")])
    is_admin = BooleanField("Admin?")
    is_courier = BooleanField("Courier?")
    office_id = SelectField("Office", coerce=int)
    submit = SubmitField('Save')

    def populate_form(self, employee):
        employee_user = employee.user
        self.email.data = employee_user.email
        self.first_name.data = employee_user.first_name
        self.last_name.data = employee_user.last_name
        self.phone_number.data = employee_user.phone_number
        self.address.data = employee_user.address
        self.is_admin.data = employee_user.has_role(Role.ADMIN)
        self.is_courier.data = employee.office_id is None
        self.office_id.data = employee.office_id

    def get_data(self):
        return (
            self.email.data,
            self.first_name.data,
            self.last_name.data,
            self.address.data,
            self.phone_number.data,
            self.is_admin.data,
            self.is_courier.data,
            self.office_id.data,
            self.password.data
        )



class EmployeeUpdateForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=20)])
    phone_number = StringField('Phone number', validators=[DataRequired(), Length(min=2, max=20)])
    is_admin = BooleanField("Admin?")
    is_courier = BooleanField("Courier?")
    office_id = SelectField("Office", coerce=int)
    submit = SubmitField('Save')

    def populate_form(self, employee):
        employee_user = employee.user
        self.email.data = employee_user.email
        self.first_name.data = employee_user.first_name
        self.last_name.data = employee_user.last_name
        self.phone_number.data = employee_user.phone_number
        self.address.data = employee_user.address
        self.is_admin.data = employee_user.has_role(Role.ADMIN)
        self.is_courier.data = employee.office_id is None
        self.office_id.data = employee.office_id

    def get_data(self):
        return (
            self.email.data,
            self.first_name.data,
            self.last_name.data,
            self.address.data,
            self.phone_number.data,
            self.is_admin.data,
            self.is_courier.data,
            self.office_id.data
        )
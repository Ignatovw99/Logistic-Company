from flask_wtf import FlaskForm
from wtforms import  Form, StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=20)])
    phone_number = StringField('Phone number', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators = [DataRequired(), Regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$", message="Password should be eight characters, at least one uppercase letter, one lowercase letter and one number")])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password', "Passwords must match")])
    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')
    
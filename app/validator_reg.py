from flask_wtf import FlaskForm
from wtforms import  Form, StringField, PasswordField, SubmitField, BooleanField, validators
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First name', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last name', validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=20)])
    phone = StringField('Phone number', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')
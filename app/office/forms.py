from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class OfficeForm(FlaskForm):
    address = StringField("Address", validators=[DataRequired("Address is required"), Length(min=2, max=200, message="Address should be between 2 and 200 symbols")])
    submit = SubmitField('Save')

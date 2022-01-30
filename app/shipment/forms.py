from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange


class ShipmentForm(FlaskForm):
    sender = StringField('Sender Email', validators=[DataRequired(), Email()])
    receiver = StringField('Receiver Email', validators=[DataRequired(), Email()])
    weight = DecimalField("Weight", validators=[DataRequired(), NumberRange(min=0.01, max=350, message="Weight should be between 0.01 kg and 350 kg")])
    delivery_address = StringField("Delivery Address")
    delivery_office_id = SelectField("Delivery Office", coerce=int, validators=[DataRequired()])

    def append_courier_fields(self):
        # TODO: sender office should be disabled for express shipments
        setattr(self, "sender_office_id", SelectField("Sender Office", validators=[DataRequired()]))
        setattr(self, "sender_address", SelectField("Sender Address", validators=[DataRequired()]))
        setattr(self, "is_express", BooleanField("Is Express?"))

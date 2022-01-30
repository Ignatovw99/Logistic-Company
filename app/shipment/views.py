from flask import Blueprint, render_template, flash

from app.auth.util import current_user, login_required, role_required
from app.common.util import find_user_by_email, persist_model
from app.models import Shipment, ShippingAddress, Role, Office, ShippingStatus
from app.office.util import find_office_by_id
from app.shipment.forms import ShipmentForm
from app.shipment.util import (
    calculate_shipment_price,
    find_employee_by_id,
    are_sender_and_delivery_addresses_different,
    find_shipments_by_employee,
    find_shipments_by_user)


shipment = Blueprint("shipment", __name__)


@shipment.route("/")
@login_required
def show():
    current_employee = find_employee_by_id(current_user.id)
    shipments = find_shipments_by_employee(current_employee) if current_employee else find_shipments_by_user(current_user)

    render_template("shipment/all.html", title="Shipments", shipments=shipments)


@shipment.route("/create", methods=["GET", "POST"])
@login_required
@role_required(Role.EMPLOYEE)
def create():
    form = ShipmentForm()

    current_employee = find_employee_by_id(current_user.id)

    if form.validate_on_submit():
        shipment = Shipment(weight=form.weight.data, acceptor=current_employee)

        users_valid = True
        sender = find_user_by_email(form.sender.data)
        if not sender:
            users_valid = False
            flash("Sender does not exists")

        receiver = find_user_by_email(form.receiver.data)
        if not receiver:
            users_valid = False
            flash("Sender does not exists")

        if users_valid:
            shipment.sender = sender
            shipment.receiver = receiver

            delivery_office = find_office_by_id(form.delivery_office_id.data)
            delivery_address = form.delivery_address.data
            to_shipping_address = ShippingAddress(address=delivery_address, office=delivery_office)
            shipment.to_address = to_shipping_address
            is_express = False

            if current_employee.is_courier():
                sender_address = form.sender_address.data
                sender_office = find_office_by_id(form.sender_office.data)
                from_shipping_address = ShippingAddress(address=sender_address, office=sender_office)
                shipment.from_address = from_shipping_address

                is_express = form.is_express.data
                if is_express:
                    shipment.transported_by = current_employee
                    if delivery_address:
                        status = ShippingStatus.TRAVELING_TO_YOUR_ADDRESS
                        shipment.deliverer = current_employee
                    else:
                        status = ShippingStatus.ON_ITS_WAY
                else:
                    status = ShippingStatus.ACCEPTED
            else:
                from_shipping_address = ShippingAddress(office=current_employee.office)
                status = ShippingStatus.READY_TO_SHIP

            shipment.status = status

            if are_sender_and_delivery_addresses_different(from_shipping_address, to_shipping_address):

                shipment.price = calculate_shipment_price(shipment, is_express)

                persist_model(from_shipping_address, commit_transaction=False)
                persist_model(to_shipping_address, commit_transaction=False)
                persist_model(shipment)
                flash("Shipment created successfully")
            else:
                flash("Sender and delivery addresses should be different")

    office_choices = [(office.id, office.address) for office in Office.query.all()]
    form.delivery_office_id.choices = office_choices

    if current_employee.is_courier():
        form.append_courier_fields()
        form.sender_office_id.data = office_choices
    
    return render_template("shipment/create.html", title="Shipment create", form=form)

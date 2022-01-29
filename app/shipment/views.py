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


@shipment.route("/create")
@login_required
@role_required(Role.EMPLOYEE)
def create():
    form = ShipmentForm()

    current_employee = find_employee_by_id(current_user.id)

    if form.validate_on_submit():
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
            if current_employee.is_courier():
                sender_address = form.sender_address.data
                sender_office = find_office_by_id(form.sender_office.data)
                from_shipping_address = ShippingAddress(address=sender_address, office=sender_office)
                status = ShippingStatus.ACCEPTED
            else:
                from_shipping_address = ShippingAddress(office=current_employee.office)
                status = ShippingStatus.READY_TO_SHIP

            delivery_office = find_office_by_id(form.delivery_office_id.data)
            to_shipping_address = ShippingAddress(address=form.delivery_address.data, office=delivery_office)

            if are_sender_and_delivery_addresses_different(from_shipping_address, to_shipping_address):
                shipment = Shipment(
                    weight=form.weight.data,
                    status=status,
                    from_address=from_shipping_address,
                    to_address=to_shipping_address, 
                    acceptor=current_employee,
                    sender=sender,
                    receiver=receiver)

                shipment.price = calculate_shipment_price(shipment)

                persist_model(from_shipping_address, commit_transaction=False)
                persist_model(to_shipping_address, commit_transaction=False)
                persist_model(shipment)
                flash("Shipment created successfully")
            else:
                flash("Sender and delivery addresses should be different")

    office_choices = [(office.id, office.address) for office in Office.query.all()]
    form.delivery_office_id.choices = office_choices

    if current_employee.is_courier():
        form.append_sender_office_field()
        form.sender_office_id.data = office_choices
    
    return render_template("shipment/create.html", title="Shipment create", form=form)

from flask import Blueprint, flash, redirect, url_for

from app.auth.util import current_user, login_required, role_required
from app.delivery.util import find_shipment_by_id
from app.shipment.util import find_employee_by_id
from app.common.util import commit_db_transaction

from app.models import Role, ShippingStatus


delivery = Blueprint("delivery", __name__)


@delivery.route("/send-for-packing/<shipment_id>")
@login_required
@role_required(Role.EMPLOYEE)
def send_for_packing(shipment_id):
    current_employee = find_employee_by_id(current_user.id)
    shipment = find_shipment_by_id(shipment_id)

    if not shipment:
        flash("Shipment does not exist", "danger")
    elif shipment.status != ShippingStatus.ACCEPTED:
        flash("Shipment cannot be sent for packing", "warning")
    elif not current_employee.is_courier() or not shipment.acceptor == current_employee:
        flash("Only the courier who accepted this shipment can send a it for packing", "warning")
    else:
        shipment.status = ShippingStatus.READY_TO_PACK
        commit_db_transaction()
        flash("Shipment was sent for packing", "success")

    return redirect(url_for("shipment.show"))


@delivery.route("/pack/<shipment_id>")
@login_required
@role_required(Role.EMPLOYEE)
def pack(shipment_id):
    current_employee = find_employee_by_id(current_user.id)
    shipment = find_shipment_by_id(shipment_id)

    if not shipment:
        flash("Shipment does not exist", "danger")
    elif shipment.status != ShippingStatus.READY_TO_PACK:
        flash("Shipment cannot be packed", "warning")
    elif shipment.from_address.office != current_employee.office:
        flash("Only an employee who works in the shipment's sender office can pack this shipment", "warning")
    else:
        shipment.status = ShippingStatus.READY_TO_SHIP
        commit_db_transaction()
        flash("Shipment was packed and it is ready for shipping", "success")

    return redirect(url_for("shipment.show"))


@delivery.route("/load/<shipment_id>")
@login_required
@role_required(Role.EMPLOYEE)
def load(shipment_id):
    current_employee = find_employee_by_id(current_user.id)
    shipment = find_shipment_by_id(shipment_id)
    
    if not shipment:
        flash("Shipment does not exist", "danger")
    elif shipment.status != ShippingStatus.READY_TO_SHIP:
        flash("Shipment cannot be loaded", "warning")
    elif not current_employee.is_courier():
        flash("Only a courier can loaded shipments", "warning")
    else:
        shipment.status = ShippingStatus.ON_ITS_WAY
        shipment.transported_by = current_employee
        commit_db_transaction()
        flash("Shipment was loaded", "success")

    return redirect(url_for("shipment.show"))


@delivery.route("/transport/<shipment_id>")
@login_required
@role_required(Role.EMPLOYEE)
def transport(shipment_id):
    current_employee = find_employee_by_id(current_user.id)
    shipment = find_shipment_by_id(shipment_id)

    if not shipment:
        flash("Shipment does not exist", "danger")
    elif shipment.status != ShippingStatus.ON_ITS_WAY:
        flash("Shipment cannot be transported", "warning")
    elif current_employee != shipment.transported_by:
        flash("Only the courier who loaded the shipment can transport it", "warning")
    else:
        shipment.status = ShippingStatus.ARRIVED
        commit_db_transaction()
        flash("Shipment was transported to the delivery destination", "success")

    return redirect(url_for("shipment.show"))


@delivery.route("/send-to-address/<shipment_id>")
@login_required
@role_required(Role.EMPLOYEE)
def send_to_address(shipment_id):
    current_employee = find_employee_by_id(current_user.id)
    shipment = find_shipment_by_id(shipment_id)

    if not shipment:
        flash("Shipment does not exist", "danger")
    elif shipment.status != ShippingStatus.ARRIVED:
        flash("Shipment cannot be shipped to the customer", "warning")
    elif not current_employee.is_courier():
        flash("Shipment cannot be shipped by an office employee", "warning")
    elif not shipment.to_address.address:
        flash("Shipment without delivery address. You cannot ship it", "warning")
    else:
        shipment.deliverer = current_employee
        shipment.status = ShippingStatus.TRAVELING_TO_YOUR_ADDRESS
        commit_db_transaction()
        flash("Shipment was sent to the delivery address", "success")
    
    return redirect(url_for("shipment.show"))


@delivery.route("/finish/<shipment_id>")
@login_required
@role_required(Role.EMPLOYEE)
def deliver_shipment(shipment_id):
    current_employee = find_employee_by_id(current_user.id)
    shipment = find_shipment_by_id(shipment_id)

    if not shipment:
        flash("Shipment does not exist", "danger")
    elif not shipment.status == ShippingStatus.ARRIVED and not shipment.status == ShippingStatus.TRAVELING_TO_YOUR_ADDRESS:
        flash("Shipment cannot be given to the customer", "warning")
    elif shipment.status == ShippingStatus.ARRIVED and current_employee.is_courier():
        flash("Shipment in status ARRIVED can be delivered only by an office employee", "warning")
    elif shipment.status == ShippingStatus.TRAVELING_TO_YOUR_ADDRESS and not shipment.deliverer == current_employee:
        flash("Shipment in status TRAVELING_TO_YOUR_ADDRESS can be delivered only by the given deliverer", "warning")
    else:
        if not shipment.deliverer:
            shipment.deliverer = current_employee
            
        shipment.status = ShippingStatus.DELIVERED
        commit_db_transaction()
        flash("Shipment was delivered to the customer", "success")
    
    return redirect(url_for("shipment.show"))

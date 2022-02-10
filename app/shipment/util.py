from flask import current_app
from sqlalchemy.orm import aliased

from app.models import Employee, Shipment, ShippingStatus, ShippingAddress, User, Role


def find_employee_by_id(id):
    return Employee.query.filter(Employee.id == id).first()


def are_sender_and_delivery_addresses_different(sender_address, delivery_address):
    return sender_address.address != delivery_address.address


def calculate_shipment_price(shipment, is_express):
    price = shipment.weight * current_app.config["PRICE_PER_KG"]
    if shipment.from_address.address:
        price = price + current_app.config["PRICE_SHIPMENT_FROM_ADDRESS"]
    if shipment.to_address.address:
        price = price + current_app.config["PRICE_SHIPMENT_TO_ADDRESS"]
    if is_express:
        express_price = current_app.config["PRICE_EXPRESS_ADDRESS"] if shipment.to_address.address else current_app.config["PRICE_EXPRESS_OFFICE"]
        price = price + express_price
    return price


def find_accepted_shipments_by_courier(employee_id):
    return Shipment.query.\
            filter((Shipment.acceptor_id == employee_id) & (Shipment.status == ShippingStatus.ACCEPTED)).\
            order_by(Shipment.sent_date.asc()).\
            all()


def find_shipments_on_its_way_by_courier(employee_id):
    return Shipment.query.\
            filter((Shipment.transported_by_id == employee_id) & (Shipment.status == ShippingStatus.ON_ITS_WAY)).\
            order_by(Shipment.sent_date.asc()).\
            all()


def find_shipments_ready_to_ship():
    return Shipment.query.\
            filter(Shipment.status == ShippingStatus.READY_TO_SHIP).\
            order_by(Shipment.sent_date.asc()).\
            all()


def find_shipments_to_deliver_from_office():
    delivery_address_alias = aliased(ShippingAddress)

    return Shipment.query.\
            filter(Shipment.status == ShippingStatus.ARRIVED).\
            join(delivery_address_alias, Shipment.to_address).\
            filter((delivery_address_alias.address != None) | (delivery_address_alias.address != "")).\
            order_by(Shipment.sent_date.asc()).\
            all()


def find_shipments_to_deliver_to_customer(employee_id):
    return Shipment.query.\
            filter((Shipment.deliverer_id == employee_id) & (Shipment.status == ShippingStatus.TRAVELING_TO_YOUR_ADDRESS)).\
            order_by(Shipment.sent_date.asc()).\
            all()


def find_shipments_in_office(office):
    from_address_alias = aliased(ShippingAddress)
    to_address_alias = aliased(ShippingAddress)

    shipments_in_office_to_pack = Shipment.query.\
            filter(Shipment.status == ShippingStatus.READY_TO_PACK).\
            join(from_address_alias, Shipment.from_address).\
            filter(from_address_alias.office_id == office.id).\
            order_by(Shipment.sent_date.asc()).\
            all()

    shipments_in_office_to_deliver = Shipment.query.\
            filter(Shipment.status == ShippingStatus.ARRIVED).\
            join(to_address_alias, Shipment.to_address).\
            filter(to_address_alias.office_id == office.id).\
            order_by(Shipment.sent_date.asc()).\
            all()

    return [*shipments_in_office_to_pack, *shipments_in_office_to_deliver]


def find_shipments_by_employee(employee):
    if employee.user.has_role(Role.ROOT):
        shipments = Shipment.query.all()
    elif employee.is_courier():
        shipments = find_accepted_shipments_by_courier(employee.id)
        shipments.extend(find_shipments_on_its_way_by_courier(employee.id))
        shipments.extend(find_shipments_to_deliver_to_customer(employee.id))
        shipments.extend(find_shipments_ready_to_ship())
        shipments.extend(find_shipments_to_deliver_from_office())
    else:
        shipments = find_shipments_in_office(employee.office)
        
    return shipments


def find_shipments_by_user(user):
    if user.has_role(Role.ROOT):
        return Shipment.query.order_by(Shipment.status.asc(), Shipment.sent_date.asc()).all()
    else:
        sender_alias = aliased(User)
        receiver_alias = aliased(User)

        return Shipment.query.\
                join(sender_alias, Shipment.sender).\
                join(receiver_alias, Shipment.receiver).\
                filter((sender_alias.id == user.id) | (receiver_alias.id == user.id)).\
                order_by(Shipment.status.asc(), Shipment.sent_date.asc()).\
                all()


def find_active_shipments_by_user(user_id):
    sender_alias = aliased(User)
    receiver_alias = aliased(User)

    return Shipment.query.\
            filter(Shipment.status != ShippingStatus.DELIVERED).\
            join(sender_alias, Shipment.sender).\
            join(receiver_alias, Shipment.receiver).\
            filter((sender_alias.id == user_id) | (receiver_alias.id == user_id)).\
            order_by(Shipment.sent_date.asc()).\
            all()

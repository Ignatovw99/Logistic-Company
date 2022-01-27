from app.models import Office, Shipment, ShippingAddress, ShippingStatus

from sqlalchemy.orm import aliased


def is_address_available(address):
    return Office.query.filter_by(address=address).first() is None


def find_office_by_id(id):
    return Office.query.filter(Office.id == id).first()


def find_all_active_shipments_by_office(office):
    from_address_alias = aliased(ShippingAddress)
    to_address_alias = aliased(ShippingAddress)

    return Shipment.query.\
            filter(Shipment.status != ShippingStatus.DELIVERED).\
            join(from_address_alias, Shipment.from_address).\
            join(to_address_alias, Shipment.to_address).\
            filter((from_address_alias.office_id == office.id) | (to_address_alias.office_id == office.id)).\
            all()

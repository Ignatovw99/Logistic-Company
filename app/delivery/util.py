from app.models import Shipment

def find_shipment_by_id(id):
    return Shipment.query.filter(Shipment.id == id).first()
    
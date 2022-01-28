from app.models import Employee, Shipment, ShippingStatus

def find_employee_by_id(id):
    return Employee.query.filter(Employee.id == id).first()
    

def find_all_active_shipments_by_employee(employee):
    return Shipment.query.\
            filter(Shipment.status != ShippingStatus.DELIVERED).\
            filter((Shipment.acceptor_id == employee.id) | (Shipment.deliverer_id == employee.id)).\
            all()
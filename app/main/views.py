from flask import Blueprint, current_app as app, render_template, jsonify, request, flash, redirect, url_for, Response
from app import db
from app import auth
from app.auth.util import current_user, anonymous_required, role_required
from app.models import User, Role, Office, ShippingStatus, Shipment, ShippingAddress, Employee

from sqlalchemy import exists, or_, and_

from fpdf import FPDF


main = Blueprint("main", __name__)


@main.route("/")
@main.route("/index")
@anonymous_required
def index():
    return render_template("main/index.html")


@main.route('/client_shipments/')
def ClientShipments():
    client = User.query.get(1);
    office_data = Office.query.all()
    status_list = [ShippingStatus.SHIPPED, ShippingStatus.DELIVERED, ShippingStatus.WAITING, ShippingStatus.ACCEPTED]
    shipments_client_data = Shipment.query.filter(or_(client == Shipment.sender,client == Shipment.receiver))
    return render_template("main/prototype/client-shipments.html", shipments_client = shipments_client_data, offices = office_data, statuses = status_list)


@main.route('/client_shipments/insert', methods=['POST'])
def insert_shipping_clients():
    if request.method == 'POST':
        weight = request.form['weight']



        if request.form['optionsFrom'] == 'address':
            from_address = request.form['fromAddressText']

        else:
            from_address = request.form['selectFromOffice']


        if request.form['optionsTo'] == 'address':
            to_address = request.form['toAddressText']

        else:
            to_address = request.form['selectToOffice']

        sender_first_name = request.form['senderFirstName']
        sender_last_name = request.form['senderLastName']
        sender_phone_number = request.form['senderPhoneNumber']
        receiver_first_name = request.form['receiverFirstName']
        receiver_last_name = request.form['receiverLastName']
        receiver_phone_number = request.form['receiverPhoneNumber']
        price = request.form['price']


        shipping_from_address = ShippingAddress(from_address)
        shipping_to_address = ShippingAddress(to_address)
        db.session.add(shipping_to_address)
        db.session.add(shipping_from_address)
        db.session.commit()

        sender = User.query.filter(and_(User.first_name == sender_first_name, User.last_name == sender_last_name,
                                          User.phone_number == sender_phone_number)).first()

        receiver = User.query.filter(and_(User.first_name == receiver_first_name, User.last_name == receiver_last_name, User.phone_number == receiver_phone_number)).first()
        acceptor = Employee.query.filter_by(id=3).first()
        deliverer = Employee.query.filter_by(id=4).first()
        status = ShippingStatus.WAITING




        shipment_data = Shipment(weight,shipping_from_address,shipping_to_address,sender,receiver,price)
        db.session.add(shipment_data)
        db.session.commit()

        flash("Shipment Inserted Successfully")

        return redirect(url_for('main.ClientShipments'))


@main.route('/client_shipments/update', methods=['GET', 'POST'])
def update_shipping_clients():
    if request.method == 'POST':
        shipping_data = Shipment.query.get(request.form.get('id'))
        shipping_data.weight = request.form['weight']


        if request.form['optionsFrom'] == 'address':
            shipping_data.from_address = ShippingAddress.query.get(request.form['fromAddressText'])
        else:
            shipping_data.from_address =ShippingAddress.query.get(request.form['selectFromOffice'])

        if request.form['optionsTo'] == 'address':
            shipping_data.to_address = ShippingAddress.query.get(request.form['toAddressText'])
        else:
            shipping_data.to_address = ShippingAddress.query.get(request.form['selectToOffice'])

        shipping_data.sender = User.query.filter(
            and_(User.first_name == request.form['senderFirstName'], User.last_name == request.form['senderLastName'],
                 User.phone_number == request.form['senderPhoneNumber'])).first()

        shipping_data.receiver = User.query.filter(and_(User.first_name == request.form['receiverFirstName'], User.last_name == request.form['receiverLastName'], User.phone_number == request.form['receiverPhoneNumber'])).first()
        shipping_data.price = request.form['price']

        db.session.commit()
        flash("Shipment Updated Successfully")

        return redirect(url_for('main.ClientShipments'))


@main.route('/client_shipments/delete/<id>/', methods=['GET', 'POST'])
def delete_shipping_clients(id):
    shipping_data = Shipment.query.get(id)

    db.session.delete(shipping_data)
    db.session.commit()
    flash("Shipment Deleted Successfully")

    return redirect(url_for('main.ClientShipments'))


@main.route('/clients')
def Clients():
    client_data =User.query.filter(~ exists().where(User.id == Employee.id))
    return render_template("main/prototype/clients.html", clients=client_data)


@main.route('/client/insert', methods=['POST'])
def insert_client():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        address = request.form['address']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        client_data = User(first_name, last_name, address, phone, email, password)
        db.session.add(client_data)
        db.session.commit()

        flash("Client added successfully.")

        return redirect(url_for('main.Clients'))


@main.route('/client/update', methods=['GET', 'POST'])
def update_client():
    if request.method == 'POST':
        client_data = User.query.get(request.form.get('id'))

        client_data.first_name = request.form['firstname']
        client_data.last_name = request.form['lastname']
        client_data.address = request.form['address']
        client_data.phone_number = request.form['phone']
        client_data.email = request.form['email']
        client_data.password = request.form['password']


        db.session.commit()
        flash("Client updated successfully.")

        return redirect(url_for('main.Clients'))


@main.route('/client/delete/<id>/', methods=['GET', 'POST'])
def delete_client(id):
    client_data = User.query.get(id)
    db.session.delete(client_data)
    db.session.commit()

    flash("Client Deleted Successfully")

    return redirect(url_for('main.Clients'))



@main.route('/shipping')
def shipment():
    all_data = Shipment.query.all()
    status_list = [ShippingStatus.SHIPPED,ShippingStatus.DELIVERED,ShippingStatus.WAITING,ShippingStatus.ACCEPTED]

    return render_template("main/prototype/shipping.html", shipments = all_data, offices = Office.query.all(), statuses = status_list)



@main.route('/shipping/employee/', methods=['POST'])
def shipments_registered_by_employee():
    employee_id = request.form['id_employee']
    employee = Employee.query.get(employee_id);

    shipments_by_employee= Shipment.query.filter(employee == Shipment.acceptor)
    return render_template("main/prototype/shipping.html", shipments = shipments_by_employee)

@main.route('/shipping',methods=['POST'])
def shipments_status():
    status_form = request.form['status_filter']

    if status_form == str(ShippingStatus.SHIPPED):
        status = ShippingStatus.SHIPPED
    elif status_form == str(ShippingStatus.DELIVERED):
        status = ShippingStatus.DELIVERED
    elif status_form == str(ShippingStatus.WAITING):
        status = ShippingStatus.WAITING
    else:
        status = ShippingStatus.ACCEPTED

    status_list = [ShippingStatus.SHIPPED, ShippingStatus.DELIVERED, ShippingStatus.WAITING, ShippingStatus.ACCEPTED]


    status_shipments= Shipment.query.filter(Shipment.status == status )

    return render_template("main/prototype/shipping.html", shipments = status_shipments, statuses = status_list)


@main.route('/shipping/shipment/', methods=['POST'])
def shipment_by_id():
    shipment_id= request.form['id_shipment']
    shipment = Shipment.query.filter_by(id=shipment_id);

    return render_template("main/prototype/shipping.html", shipments = shipment)



@main.route('/shipping/sender/', methods=['POST'])
def send_by_client_shipments():
    sender_id= request.form['id_sender']
    client = User.query.get(sender_id);


    shipments_by_sender= Shipment.query.filter(client == Shipment.sender)
    return render_template("main/prototype/shipping.html", shipments = shipments_by_sender)

@main.route('/shipping/receiver/', methods=['POST'])
def received_by_client_shipments():
    receiver_id = request.form['id_receiver']
    client = User.query.get(receiver_id);

    shipments_by_receiver= Shipment.query.filter(client == Shipment.receiver)
    return render_template("main/prototype/shipping.html", shipments = shipments_by_receiver)

@main.route('/shipping/insert', methods=['POST'])
def insert_shipping():
    if request.method == 'POST':
        weight = request.form['weight']
        status_value = request.form['status']


        if request.form['optionsFrom'] == 'address':
            from_address = request.form['fromAddressText']

        else:
            from_address = request.form['selectFromOffice']


        if request.form['optionsTo'] == 'address':
            to_address = request.form['toAddressText']

        else:
            to_address = request.form['selectToOffice']


        sender_first_name = request.form['senderFirstName']
        sender_last_name = request.form['senderLastName']
        sender_phone_number = request.form['senderPhoneNumber']
        receiver_first_name = request.form['receiverFirstName']
        receiver_last_name = request.form['receiverLastName']
        receiver_phone_number = request.form['receiverPhoneNumber']
        acceptor = request.form['acceptor']
        deliverer = request.form['deliverer']
        price = request.form['price']
        status = []

        if status_value == '1':
            status.append(ShippingStatus.SHIPPED)
        elif status_value == '2':
            status.append(ShippingStatus.DELIVERED)
        elif status_value == '3':
            status.append(ShippingStatus.WAITING)
        else:
            status.append(ShippingStatus.ACCEPTED)

        shipping_from_address = ShippingAddress(from_address)
        shipping_to_address = ShippingAddress(to_address)
        db.session.add(shipping_to_address)
        db.session.add(shipping_from_address)
        db.session.commit()

        sender_id = User.query.filter(and_(User.first_name == sender_first_name, User.last_name == sender_last_name, User.phone_number == sender_phone_number)).first()
        receiver_id = User.query.filter(and_(User.first_name == receiver_first_name, User.last_name == receiver_last_name, User.phone_number == receiver_phone_number)).first()
        acceptor_id = Employee.query.filter_by(id=acceptor).first()
        deliverer_id = Employee.query.filter_by(id=deliverer).first()


        shipment_data = Shipment(weight, shipping_from_address, shipping_to_address, sender_id, receiver_id,price, acceptor_id, deliverer_id,status[0])
        db.session.add(shipment_data)
        db.session.commit()

        flash("Shipment Inserted Successfully")

        return redirect(url_for('main.shipment'))



@main.route('/shipping/update', methods=['GET', 'POST'])
def update_shipping():
    if request.method == 'POST':
        shipping_data = Shipment.query.get(request.form.get('id'))
        shipping_data.weight = request.form['weight']
        if request.form['status'] == '1':
            shipping_data.status = ShippingStatus.SHIPPED
        elif request.form['status'] == '2' :
            shipping_data.status = ShippingStatus.DELIVERED
        elif request.form['status'] == '3' :
            shipping_data.status = ShippingStatus.WAITING
        else:
            shipping_data.status = ShippingStatus.ACCEPTED


        if request.form['optionsFrom'] == 'address':
            shipping_data.from_address = ShippingAddress.query.get(request.form['fromAddressText'])
        else:
            shipping_data.from_address =ShippingAddress.query.get(request.form['selectFromOffice'])

        if request.form['optionsTo'] == 'address':
            shipping_data.to_address = ShippingAddress.query.get(request.form['toAddressText'])
        else:
            shipping_data.to_address = ShippingAddress.query.get(request.form['selectToOffice'])


        shipping_data.sender = User.query.filter(and_(User.first_name == request.form['senderFirstName'], User.last_name == request.form['senderLastName'], User.phone_number == request.form['senderPhoneNumber'])).first()

        shipping_data.receiver = User.query.filter(and_(User.first_name == request.form['receiverFirstName'], User.last_name == request.form['receiverLastName'], User.phone_number == request.form['receiverPhoneNumber'])).first()
        shipping_data.acceptor = Employee.query.get(request.form['acceptor'])
        shipping_data.deliverer = Employee.query.get(request.form['deliverer'])
        shipping_data.price = request.form['price']

        db.session.commit()
        flash("Shipment Updated Successfully")

        return redirect(url_for('main.shipment'))



@main.route('/shipping/delete/<id>/', methods=['GET', 'POST'])
def delete_shipping(id):
    shipping_data = Shipment.query.get(id)

    db.session.delete(shipping_data)
    db.session.commit()
    flash("Shipment Deleted Successfully")

    return redirect(url_for('main.shipment'))

# ------------------------------R e p o r t s----------------------------------------------------------


@main.route('/download/report/employees/pdf')
def download_report_employees():
    result = Employee.query.all()
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w

    pdf.set_font('Times', 'B', 12)
    pdf.cell(page_width, 0.0, 'Employees Data', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 8)

    col_width = page_width / 30

    pdf.ln(1)

    th = pdf.font_size

    for row in result:
        pdf.cell(col_width, th, "ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.user.id))
        pdf.ln(th)
        pdf.cell(col_width, th, "First Name")
        pdf.ln(th)
        pdf.cell(col_width, th, row.user.first_name)
        pdf.ln(th)
        pdf.cell(col_width, th, "Last Name")
        pdf.ln(th)
        pdf.cell(col_width, th, row.user.last_name)
        pdf.ln(th)
        pdf.cell(col_width, th, "Address")
        pdf.ln(th)
        pdf.cell(col_width, th, row.user.address)
        pdf.ln(th)
        pdf.cell(col_width, th, "Phone")
        pdf.ln(th)
        pdf.cell(col_width, th, row.user.phone_number)
        pdf.ln(th)
        pdf.cell(col_width, th, "Email")
        pdf.ln(th)
        pdf.cell(col_width, th, row.user.email)
        pdf.ln(th)
        pdf.cell(col_width, th, "Office ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.office_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)



    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=employees_report.pdf'})


@main.route('/download/report/clients/pdf')
def download_report_clients():
    result = User.query.filter(~ exists().where(User.id == Employee.id))
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w

    pdf.set_font('Times', 'B', 12)
    pdf.cell(page_width, 0.0, 'Clients Data', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 8)

    col_width = page_width / 30

    pdf.ln(1)

    th = pdf.font_size

    for row in result:
        pdf.cell(col_width, th, "ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.id))
        pdf.ln(th)
        pdf.cell(col_width, th, "First Name")
        pdf.ln(th)
        pdf.cell(col_width, th, row.first_name)
        pdf.ln(th)
        pdf.cell(col_width, th, "Last Name")
        pdf.ln(th)
        pdf.cell(col_width, th, row.last_name)
        pdf.ln(th)
        pdf.cell(col_width, th, "Address")
        pdf.ln(th)
        pdf.cell(col_width, th, row.address)
        pdf.ln(th)
        pdf.cell(col_width, th, "Phone")
        pdf.ln(th)
        pdf.cell(col_width, th, row.phone_number)
        pdf.ln(th)
        pdf.cell(col_width, th, "Email")
        pdf.ln(th)
        pdf.cell(col_width, th, row.email)
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)


    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=clients_report.pdf'})


@main.route('/download/report/shipments/pdf')
def download_report_shipments():
    result =Shipment.query.all()
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w

    pdf.set_font('Times', 'B', 12)
    pdf.cell(page_width, 0.0, 'Shipments Data', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 7)

    col_width = page_width / 30

    pdf.ln(1)

    th = pdf.font_size

    for row in result:
        pdf.cell(col_width, th, "ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.id))
        pdf.ln(th)
        pdf.cell(col_width, th, "Weight")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.weight))
        pdf.ln(th)
        pdf.cell(col_width, th, "Status")
        pdf.ln(th)
        pdf.cell(col_width * 7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.from_address_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "To Address ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.to_address_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "Sender")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.sender))
        pdf.ln(th)
        pdf.cell(col_width, th, "Receiver")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.receiver))
        pdf.ln(th)
        pdf.cell(col_width, th, "Acceptor")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.acceptor))
        pdf.ln(th)
        pdf.cell(col_width, th, "Deliverer")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.deliverer))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)


    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=shipments_report.pdf'})


@main.route('/download/report/shipments-by-employee/pdf', methods=['GET', 'POST'])
def download_report_shipments_by_employee():
    employee_id = request.form['id_employee']
    employee = Employee.query.get(employee_id);

    result = Shipment.query.filter(employee == Shipment.acceptor)
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w

    pdf.set_font('Times', 'B', 12)
    pdf.cell(page_width, 0.0, 'Shipments Data', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 7)

    col_width = page_width / 30

    pdf.ln(1)

    th = pdf.font_size

    for row in result:
        pdf.cell(col_width, th, "ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.id))
        pdf.ln(th)
        pdf.cell(col_width, th, "Weight")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.weight))
        pdf.ln(th)
        pdf.cell(col_width, th, "Status")
        pdf.ln(th)
        pdf.cell(col_width * 7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.from_address_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "To Address ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.to_address_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "Sender")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.sender))
        pdf.ln(th)
        pdf.cell(col_width, th, "Receiver")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.receiver))
        pdf.ln(th)
        pdf.cell(col_width, th, "Acceptor")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.acceptor))
        pdf.ln(th)
        pdf.cell(col_width, th, "Deliverer")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.deliverer))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)



    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=shipments_by_employee_report.pdf'})

@main.route('/download/report/shipments-by-sender/pdf',methods=['GET', 'POST'])
def download_report_shipments_by_sender():
    sender_id = request.form['id_sender']
    client = User.query.get(sender_id);

    result = Shipment.query.filter(client == Shipment.sender)
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w

    pdf.set_font('Times', 'B', 12)
    pdf.cell(page_width, 0.0, 'Shipments Data', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 7)

    col_width = page_width / 30

    pdf.ln(1)

    th = pdf.font_size

    for row in result:
        pdf.cell(col_width, th, "ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.id))
        pdf.ln(th)
        pdf.cell(col_width, th, "Weight")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.weight))
        pdf.ln(th)
        pdf.cell(col_width, th, "Status")
        pdf.ln(th)
        pdf.cell(col_width * 7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.from_address_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "To Address ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.to_address_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "Sender")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.sender))
        pdf.ln(th)
        pdf.cell(col_width, th, "Receiver")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.receiver))
        pdf.ln(th)
        pdf.cell(col_width, th, "Acceptor")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.acceptor))
        pdf.ln(th)
        pdf.cell(col_width, th, "Deliverer")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.deliverer))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)



    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=shipments_by_sender_report.pdf'})



@main.route('/download/report/', methods=['GET', 'POST'])
def download_report():
    status_list = [ShippingStatus.SHIPPED, ShippingStatus.DELIVERED, ShippingStatus.WAITING, ShippingStatus.ACCEPTED]
    return render_template("main/prototype/download.html",statuses = status_list)



@main.route('/download/report/shipments-by-receiver/pdf', methods=['GET', 'POST'])
def download_report_shipments_by_receiver():
    receiver_id = request.form['id_receiver']
    client = User.query.get(receiver_id);

    result = Shipment.query.filter(client == Shipment.receiver)
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w

    pdf.set_font('Times', 'B', 12)
    pdf.cell(page_width, 0.0, 'Shipments Data', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 7)

    col_width = page_width / 30

    pdf.ln(1)

    th = pdf.font_size

    for row in result:
        pdf.cell(col_width, th, "ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.id) )
        pdf.ln(th)
        pdf.cell(col_width, th, "Weight")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.weight))
        pdf.ln(th)
        pdf.cell(col_width, th, "Status")
        pdf.ln(th)
        pdf.cell(col_width*7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.from_address_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "To Address ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.to_address_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "Sender")
        pdf.ln(th)
        pdf.cell(col_width*15, th, str(row.sender))
        pdf.ln(th)
        pdf.cell(col_width, th, "Receiver")
        pdf.ln(th)
        pdf.cell(col_width*15, th, str(row.receiver))
        pdf.ln(th)
        pdf.cell(col_width, th, "Acceptor")
        pdf.ln(th)
        pdf.cell(col_width*15, th, str(row.acceptor))
        pdf.ln(th)
        pdf.cell(col_width, th, "Deliverer")
        pdf.ln(th)
        pdf.cell(col_width*15, th, str(row.deliverer))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)


    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=shipments_by_receiver_report.pdf'})


@main.route('/download/report/shipments-by-status/pdf', methods=['GET', 'POST'])
def download_report_shipments_by_status():
    status_form = request.form['status_filter']

    if status_form == str(ShippingStatus.SHIPPED):
        status = ShippingStatus.SHIPPED
    elif status_form == str(ShippingStatus.DELIVERED):
        status = ShippingStatus.DELIVERED
    elif status_form == str(ShippingStatus.WAITING):
        status = ShippingStatus.WAITING
    else:
        status = ShippingStatus.ACCEPTED

    result = Shipment.query.filter(Shipment.status == status)
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w

    pdf.set_font('Times', 'B', 12)
    pdf.cell(page_width, 0.0, 'Shipments Data', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 7)

    col_width = page_width / 30

    pdf.ln(1)

    th = pdf.font_size

    for row in result:
        pdf.cell(col_width, th, "ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.id))
        pdf.ln(th)
        pdf.cell(col_width, th, "Weight")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.weight))
        pdf.ln(th)
        pdf.cell(col_width, th, "Status")
        pdf.ln(th)
        pdf.cell(col_width * 7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.from_address_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "To Address ID")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.to_address_id))
        pdf.ln(th)
        pdf.cell(col_width, th, "Sender")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.sender))
        pdf.ln(th)
        pdf.cell(col_width, th, "Receiver")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.receiver))
        pdf.ln(th)
        pdf.cell(col_width, th, "Acceptor")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.acceptor))
        pdf.ln(th)
        pdf.cell(col_width, th, "Deliverer")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.deliverer))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)


    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=shipments_by_status_report.pdf'})

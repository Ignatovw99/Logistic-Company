import enum

from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy.orm import relationship, joinedload, session, Load, contains_eager

app = Flask(__name__)
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logisticCompany.db'
db = SQLAlchemy(app)

app.secret_key = "Secret Key"


@app.before_first_request
def create_tables():
    db.create_all()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(60), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)


    def __init__(self, first_name, last_name, address, phone_number, email, password):
        super(User, self).__init__()

        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.phone_number = phone_number
        self.email = email
        self.password = password

    def __repr__(self):
        return f"User(first_name={self.first_name}, last_name={self.last_name})"


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    office_id = db.Column(db.Integer, db.ForeignKey("offices.id"))

    user = db.relationship(User, foreign_keys=id, lazy="joined")

    def __init__(self, user_id, office_id):
        super(Employee, self).__init__()
        self.id = user_id
        self.office_id = office_id


    def __repr__(self):
        return f"Employee(first_name={self.user.first_name}, last_name={self.user.last_name}, office_id={self.office_id})"





class Office(db.Model):
    __tablename__ = "offices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    address = db.Column(db.String(200), nullable=False)

    employees = db.relationship(Employee, backref="office", lazy="select", cascade="all,delete-orphan", single_parent=True)

    def __init__(self, name, address):
        super(Office, self).__init__()
        self.name = name
        self.address = address

    def __repr__(self):
        return f"Office(name={self.name}, address={self.address}, employees{self.employees})"

class ShippingStatus(enum.Enum):
    SHIPPED = 1
    DELIVERED = 2


class ShippingAddress(db.Model):
    __tablename__ = "shipping_addresses"

    id = db.Column(db.Integer, primary_key=True)
    office_id = db.Column(db.Integer, db.ForeignKey("offices.id"))
    address = db.Column(db.String(200))

    office = db.relationship(Office, foreign_keys=office_id, lazy="joined", cascade="all,delete-orphan", single_parent=True)
    def __init__(self, address='',office_id=0):
        self.address = address
        self.office_id = office_id

    def __repr__(self):
        return f"ShippingAddress(office_id={self.office_id}, address={self.address})"


class Shipment(db.Model):
    __tablename__ = "shipments"

    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(ShippingStatus), nullable=False, default=ShippingStatus.SHIPPED)
    from_address_id = db.Column(db.Integer, db.ForeignKey("shipping_addresses.id"), nullable=False, unique=True)
    to_address_id = db.Column(db.Integer, db.ForeignKey("shipping_addresses.id"), nullable=False, unique=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    acceptor_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    deliverer_id = db.Column(db.Integer, db.ForeignKey("employees.id"))

    from_address = db.relationship(ShippingAddress, foreign_keys=from_address_id, uselist=False, lazy="select")
    to_address = db.relationship(ShippingAddress, foreign_keys=to_address_id, uselist=False, lazy="select")
    sender = db.relationship(User, foreign_keys=sender_id, lazy="select")
    receiver = db.relationship(User, foreign_keys=receiver_id, lazy="select")
    acceptor = db.relationship(Employee, foreign_keys=acceptor_id, lazy="select")
    deliverer = db.relationship(Employee, foreign_keys=deliverer_id, lazy="select")

    def __init__(self, weight,status, from_address,to_address, sender,receiver, acceptor, deliverer):
        self.weight = weight
        self.status = status
        self.from_address = from_address
        self.to_address = to_address
        self.sender = sender
        self.receiver = receiver
        self.acceptor = acceptor
        self.deliverer = deliverer

    def __repr__(self):
        return f"Shipment(weight={self.weight}, status={self.status})"


@app.route('/shipping')
def shipment():
    all_data = Shipment.query.all()
    status_list = [ShippingStatus.SHIPPED,ShippingStatus.DELIVERED]

    return render_template("shipping.html", shipments = all_data, offices = Office.query.all(), statuses = status_list)

@app.route('/client_shipments/<id>/')
def client_shipments(id):
    client = User.query.get(id);

    shipments_client_data = Shipment.query.filter(or_(client == Shipment.sender,client == Shipment.receiver))
    return render_template("client-shipments.html", shipments_client = shipments_client_data)

@app.route('/shipping/employee/', methods=['POST'])
def shipments_registered_by_employee():
    employee_id = request.form['id_employee']
    employee = Employee.query.get(employee_id);

    shipments_by_employee= Shipment.query.filter(employee == Shipment.acceptor)
    return render_template("shipping.html", shipments = shipments_by_employee)

@app.route('/shipping/status/',methods=['POST'])
def shipments_status():
    status_form = request.form['status_filter']

    if status_form == str(ShippingStatus.SHIPPED):
        status = ShippingStatus.SHIPPED
    else:
        status = ShippingStatus.DELIVERED

    status_shipments= Shipment.query.filter(Shipment.status == status )
    return render_template("shipping.html", shipments = status_shipments)


@app.route('/shipping/sender/', methods=['POST'])
def send_by_client_shipments():
    sender_id= request.form['id_sender']
    client = User.query.get(sender_id);

    shipments_by_sender= Shipment.query.filter(client == Shipment.sender)
    return render_template("shipping.html", shipments = shipments_by_sender)

@app.route('/shipping/receiver/', methods=['POST'])
def received_by_client_shipments():
    receiver_id = request.form['id_receiver']
    client = User.query.get(receiver_id);

    shipments_by_receiver= Shipment.query.filter(client == Shipment.receiver)
    return render_template("shipping.html", shipments = shipments_by_receiver)


@app.route('/shipping/insert', methods=['POST'])
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

        sender = request.form['sender']
        receiver = request.form['receiver']
        acceptor = request.form['acceptor']
        deliverer = request.form['deliverer']
        status = []

        if status_value == 1:
            status.append(ShippingStatus.SHIPPED)
        else:
            status.append(ShippingStatus.DELIVERED)




        shipping_from_address = ShippingAddress(from_address)
        shipping_to_address = ShippingAddress(to_address)
        db.session.add(shipping_to_address)
        db.session.add(shipping_from_address)
        db.session.commit()
        # from_id =ShippingAddress.query.filter_by(address=from_address).first()
        # to_id =ShippingAddress.query.filter_by(address=to_address).first()
        sender_id = User.query.filter_by(id=sender).first()
        receiver_id = User.query.filter_by(id=receiver).first()
        acceptor_id = Employee.query.filter_by(id=acceptor).first()
        deliverer_id = Employee.query.filter_by(id=deliverer).first()


        shipment_data = Shipment(weight,status[0], shipping_from_address, shipping_to_address, sender_id, receiver_id, acceptor_id, deliverer_id)
        db.session.add(shipment_data)
        db.session.commit()

        flash("Shipment Inserted Successfully")

        return redirect(url_for('shipment'))



@app.route('/shipping/update', methods=['GET', 'POST'])
def update_shipping():
    if request.method == 'POST':
        shipping_data = Shipment.query.get(request.form.get('id'))
        shipping_data.weight = request.form['weight']
        if request.form['status'] == '1':
            shipping_data.status = ShippingStatus.SHIPPED
        else:
            shipping_data.status = ShippingStatus.DELIVERED
        if request.form['optionsFrom'] == 'address':
            shipping_data.from_address = ShippingAddress.query.get(request.form['fromAddressText'])
        else:
            shipping_data.from_address =ShippingAddress.query.get(request.form['selectFromOffice'])

        if request.form['optionsTo'] == 'address':
            shipping_data.to_address = ShippingAddress.query.get(request.form['toAddressText'])
        else:
            shipping_data.to_address = ShippingAddress.query.get(request.form['selectToOffice'])
        shipping_data.sender = User.query.get(request.form['sender'])
        shipping_data.receiver = User.query.get(request.form['receiver'])
        shipping_data.acceptor = Employee.query.get(request.form['acceptor'])
        shipping_data.deliverer = Employee.query.get(request.form['deliverer'])

        db.session.commit()
        flash("Shipment Updated Successfully")

        return redirect(url_for('shipment'))



@app.route('/shipping/delete/<id>/', methods=['GET', 'POST'])
def delete_shipping(id):
    shipping_data = Shipment.query.get(id)

    db.session.delete(shipping_data)
    db.session.commit()
    flash("Shipment Deleted Successfully")

    return redirect(url_for('shipment'))



@app.route('/offices')
def Offices():
    all_data = Office.query.all()

    return render_template("offices.html", offices=all_data)



@app.route('/offices/insert', methods=['POST'])
def insert_office():
    if request.method == 'POST':
        office_name = request.form['officename']
        office_address = request.form['officeaddress']

        office_data = Office(office_name, office_address)
        db.session.add(office_data)
        db.session.commit()

        flash("Office Inserted Successfully")

        return redirect(url_for('Offices'))



@app.route('/offices/update', methods=['GET', 'POST'])
def update_office():
    if request.method == 'POST':
        office_data = Office.query.get(request.form.get('id'))
        office_data.name = request.form['officename']
        office_data.address = request.form['officeaddress']

        db.session.commit()
        flash("Office Updated Successfully")

        return redirect(url_for('Offices'))



@app.route('/offices/delete/<id>/', methods=['GET', 'POST'])
def delete_office(id):
    office_data = Office.query.get(id)

    db.session.delete(office_data)
    db.session.commit()
    flash("Office Deleted Successfully")

    return redirect(url_for('Offices'))


@app.route('/employees')
def Employees():
    employees_data =Employee.query.all()


    return render_template("employees.html", employees=employees_data)


@app.route('/employees/insert', methods=['POST'])
def insert_employee():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        address = request.form['address']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        office_id = request.form['officeid']

        exists = db.session.query(Office.id).filter_by(id=office_id).first()
        if exists is not None:
             user_data = User(first_name, last_name, address, phone, email, password)
             db.session.add(user_data)
             db.session.commit()
             employee_data = Employee(user_data.id, office_id)
             db.session.add(employee_data)
             db.session.commit()

        else:
            flash("This office ID does not exist. Try again.", 'error')

        return redirect(url_for('Employees'))



@app.route('/employees/update', methods=['GET', 'POST'])
def update_employee():
    if request.method == 'POST':
        employee_data = Employee.query.get(request.form.get('id'))

        employee_data.user.first_name = request.form['firstname']
        employee_data.user.last_name = request.form['lastname']
        employee_data.user.address = request.form['address']
        employee_data.user.phone = request.form['phone']
        employee_data.user.email = request.form['email']
        employee_data.user.password = request.form['password']
        employee_data.office_id = request.form['officeid']

        db.session.commit()
        flash("Employee Updated Successfully")

        return redirect(url_for('Employees'))


@app.route('/employees/delete/<id>/', methods=['GET', 'POST'])
def delete_employee(id):
    employee_data = Employee.query.get(id)
    user_data = User.query.get(id)
    db.session.delete(employee_data)
    db.session.delete(user_data)
    db.session.commit()

    flash("Employee Deleted Successfully")

    return redirect(url_for('Employees'))

@app.route('/clients')
def Clients():
    client_data =User.query.filter(~ exists().where(User.id == Employee.id))


    return render_template("clients.html", clients=client_data)


@app.route('/client/insert', methods=['POST'])
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

        return redirect(url_for('Clients'))



@app.route('/client/update', methods=['GET', 'POST'])
def update_client():
    if request.method == 'POST':
        client_data = User.query.get(request.form.get('id'))

        client_data.first_name = request.form['firstname']
        client_data.last_name = request.form['lastname']
        client_data.address = request.form['address']
        client_data.phone = request.form['phone']
        client_data.email = request.form['email']
        client_data.password = request.form['password']


        db.session.commit()
        flash("Client updated successfully.")

        return redirect(url_for('Clients'))


@app.route('/client/delete/<id>/', methods=['GET', 'POST'])
def delete_client(id):
    client_data = User.query.get(id)
    db.session.delete(client_data)
    db.session.commit()

    flash("Client Deleted Successfully")

    return redirect(url_for('Clients'))




# ------------------------------R e p o r t s----------------------------------------------------------


@app.route('/download/report/employees/pdf')
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


@app.route('/download/report/clients/pdf')
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


@app.route('/download/report/shipments/pdf')
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


@app.route('/download/report/shipments-by-employee/pdf', methods=['GET', 'POST'])
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

@app.route('/download/report/shipments-by-sender/pdf',methods=['GET', 'POST'])
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



@app.route('/download/report/', methods=['GET', 'POST'])
def download_report():
    status_list = [ShippingStatus.SHIPPED, ShippingStatus.DELIVERED]
    return render_template("download.html",statuses = status_list)



@app.route('/download/report/shipments-by-receiver/pdf', methods=['GET', 'POST'])
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


@app.route('/download/report/shipments-by-status/pdf' ,methods=['GET', 'POST'])
def download_report_shipments_by_status():
    status_form = request.form['status_filter']

    if status_form == str(ShippingStatus.SHIPPED):
        status = ShippingStatus.SHIPPED
    else:
        status = ShippingStatus.DELIVERED

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





if __name__ == "__main__":

    app.run(debug=True)

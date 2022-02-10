from flask import Blueprint, current_app as app, render_template, jsonify, request, flash, redirect, url_for, Response
from app import csrf
from app import auth
from app.auth.util import current_user, anonymous_required, login_required, role_required
from app.models import User, Role, Office, ShippingStatus, Shipment, ShippingAddress, Employee

from sqlalchemy import exists, or_, and_

from fpdf import FPDF


main = Blueprint("main", __name__)


@main.route("/")
@main.route("/index")
@anonymous_required
def index():
    return render_template("main/index.html")

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
        if row.user.address:
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
        pdf.cell(col_width, th, "Date")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.sent_date))
        pdf.ln(th)
        pdf.cell(col_width, th, "Weight")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.weight))
        pdf.ln(th)
        pdf.cell(col_width, th, "Status")
        pdf.ln(th)
        pdf.cell(col_width * 7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.from_address.address))
        pdf.ln(th)
        pdf.cell(col_width, th, "To Address")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.to_address.address))
        pdf.ln(th)
        pdf.cell(col_width, th, "Sender")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(str(row.sender.id) + " "+ row.sender.first_name + " " + row.sender.last_name ))
        pdf.ln(th)
        pdf.cell(col_width, th, "Receiver")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(str(row.receiver.id) + " "+ row.receiver.first_name + " " + row.receiver.last_name ))
        pdf.ln(th)
        pdf.cell(col_width, th, "Acceptor")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.acceptor))
        pdf.ln(th)
        pdf.cell(col_width, th, "Deliverer")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.deliverer))
        pdf.ln(th)
        pdf.cell(col_width, th, "Transported by")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.transported_by))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)


    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=shipments_report.pdf'})


@main.route('/download/report/shipments-by-employee/pdf', methods=['GET', 'POST'])
@csrf.exempt
def download_report_shipments_by_employee():
    employee_email = request.form['email_employee']
    user = User.query.filter_by(email=employee_email).first()
    employee = Employee.query.filter(Employee.user == user).first()
    if not employee:
        flash("Employee does not exist", "danger")
        return redirect(url_for("main.download_report"))

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
        pdf.cell(col_width, th, "Date")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.sent_date))
        pdf.ln(th)
        pdf.cell(col_width, th, "Weight")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.weight))
        pdf.ln(th)
        pdf.cell(col_width, th, "Status")
        pdf.ln(th)
        pdf.cell(col_width * 7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address ")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.from_address.address))
        pdf.ln(th)
        pdf.cell(col_width, th, "To Address ")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.to_address.address))
        pdf.ln(th)
        pdf.cell(col_width, th, "Sender")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(str(row.sender.id) + " " + row.sender.first_name + " " + row.sender.last_name))
        pdf.ln(th)
        pdf.cell(col_width, th, "Receiver")
        pdf.ln(th)
        pdf.cell(col_width * 15, th,str(str(row.receiver.id) + " " + row.receiver.first_name + " " + row.receiver.last_name))
        pdf.ln(th)
        pdf.cell(col_width, th, "Acceptor")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.acceptor))
        pdf.ln(th)
        pdf.cell(col_width, th, "Deliverer")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.deliverer))
        pdf.ln(th)
        pdf.cell(col_width, th, "Transported by")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.transported_by))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)

    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=shipments_by_employee_report.pdf'})


@main.route('/download/report/shipments-by-sender/pdf',methods=['GET', 'POST'])
@csrf.exempt
def download_report_shipments_by_sender():
    sender_email= request.form['email_sender']
    client = User.query.filter_by(email = sender_email).first()
    if not client:
        flash("Sender does not exist", "danger")
        return redirect(url_for("main.download_report"))

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
        pdf.cell(col_width, th, "Date")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.sent_date))
        pdf.ln(th)
        pdf.cell(col_width, th, "Weight")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.weight))
        pdf.ln(th)
        pdf.cell(col_width, th, "Status")
        pdf.ln(th)
        pdf.cell(col_width * 7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address ")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.from_address.address))
        pdf.ln(th)
        pdf.cell(col_width, th, "To Address ")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.to_address.address))
        pdf.ln(th)
        pdf.cell(col_width, th, "Sender")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(str(row.sender.id) + " " + row.sender.first_name + " " + row.sender.last_name))
        pdf.ln(th)
        pdf.cell(col_width, th, "Receiver")
        pdf.ln(th)
        pdf.cell(col_width * 15, th,str(str(row.receiver.id) + " " + row.receiver.first_name + " " + row.receiver.last_name))
        pdf.ln(th)
        pdf.cell(col_width, th, "Acceptor")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.acceptor))
        pdf.ln(th)
        pdf.cell(col_width, th, "Deliverer")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.deliverer))
        pdf.ln(th)
        pdf.cell(col_width, th, "Transported by")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.transported_by))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)



    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=shipments_by_sender_report.pdf'})



@main.route('/download/report/', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN)
@csrf.exempt
def download_report():
    status_list = [ShippingStatus.ACCEPTED, ShippingStatus.READY_TO_PACK, ShippingStatus.READY_TO_SHIP,ShippingStatus.ON_ITS_WAY,
                   ShippingStatus.ARRIVED, ShippingStatus.TRAVELING_TO_YOUR_ADDRESS,ShippingStatus.DELIVERED]
    return render_template("main/download.html",statuses = status_list)



@main.route('/download/report/shipments-by-receiver/pdf', methods=['GET', 'POST'])
@csrf.exempt
def download_report_shipments_by_receiver():
    receiver_email = request.form['email_receiver']
    client = User.query.filter_by(email = receiver_email).first()
    
    if not client:
        flash("Receiver does not exist", "danger")
        return redirect(url_for("main.download_report"))

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
        pdf.cell(col_width, th, "Date")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.sent_date))
        pdf.ln(th)
        pdf.cell(col_width, th, "Weight")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.weight))
        pdf.ln(th)
        pdf.cell(col_width, th, "Status")
        pdf.ln(th)
        pdf.cell(col_width*7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address ")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.from_address.address))
        pdf.ln(th)
        pdf.cell(col_width, th, "To Address ")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.to_address.address))
        pdf.ln(th)
        pdf.cell(col_width, th, "Sender")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(str(row.sender.id) + " " + row.sender.first_name + " " + row.sender.last_name))
        pdf.ln(th)
        pdf.cell(col_width, th, "Receiver")
        pdf.ln(th)
        pdf.cell(col_width * 15, th,str(str(row.receiver.id) + " " + row.receiver.first_name + " " + row.receiver.last_name))
        pdf.ln(th)
        pdf.cell(col_width, th, "Acceptor")
        pdf.ln(th)
        pdf.cell(col_width*15, th, str(row.acceptor))
        pdf.ln(th)
        pdf.cell(col_width, th, "Deliverer")
        pdf.ln(th)
        pdf.cell(col_width*15, th, str(row.deliverer))
        pdf.ln(th)
        pdf.cell(col_width, th, "Transported by")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.transported_by))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)


    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=shipments_by_receiver_report.pdf'})


@main.route('/download/report/shipments-by-status/pdf', methods=['GET', 'POST'])
@csrf.exempt
def download_report_shipments_by_status():
    status_form = request.form['status_filter']

    if status_form == str(ShippingStatus.ACCEPTED):
        status = ShippingStatus.ACCEPTED
    elif status_form == str(ShippingStatus.READY_TO_PACK):
        status = ShippingStatus.READY_TO_PACK
    elif status_form == str(ShippingStatus.READY_TO_SHIP):
        status = ShippingStatus.READY_TO_SHIP
    elif status_form == str(ShippingStatus.ON_ITS_WAY):
        status = ShippingStatus.ON_ITS_WAY
    elif status_form == str(ShippingStatus.ARRIVED):
        status = ShippingStatus.ARRIVED
    elif status_form == str(ShippingStatus.DELIVERED):
        status = ShippingStatus.DELIVERED
    else:
        status = ShippingStatus.TRAVELING_TO_YOUR_ADDRESS

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
        pdf.cell(col_width, th, "Date")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.sent_date))
        pdf.ln(th)
        pdf.cell(col_width, th, "Weight")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.weight))
        pdf.ln(th)
        pdf.cell(col_width, th, "Status")
        pdf.ln(th)
        pdf.cell(col_width * 7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.from_address.address))
        pdf.ln(th)
        pdf.cell(col_width, th, "To Address")
        pdf.ln(th)
        pdf.cell(col_width, th, str(row.to_address.address))
        pdf.ln(th)
        pdf.cell(col_width, th, "Sender")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(str(row.sender.id) + " " + row.sender.first_name + " " + row.sender.last_name))
        pdf.ln(th)
        pdf.cell(col_width, th, "Receiver")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(str(row.receiver.id) + " " + row.receiver.first_name + " " + row.receiver.last_name))
        pdf.ln(th)
        pdf.cell(col_width, th, "Acceptor")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.acceptor))
        pdf.ln(th)
        pdf.cell(col_width, th, "Deliverer")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.deliverer))
        pdf.ln(th)
        pdf.cell(col_width, th, "Transported by")
        pdf.ln(th)
        pdf.cell(col_width * 15, th, str(row.transported_by))
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)


    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=shipments_by_status_report.pdf'})


@main.route('/download/report/company-revenue/pdf', methods=['GET', 'POST'])
@csrf.exempt
def download_report_logistic_company_revenue():
    revenue = 0.0
    result = Shipment.query.filter_by(status=ShippingStatus.DELIVERED).all()
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w

    pdf.set_font('Times', 'B', 12)
    pdf.cell(page_width, 0.0, 'Shipments Data', align='C')
    pdf.ln(10)

    pdf.set_font('Courier', '', 7)

    col_width = page_width /10

    pdf.ln(1)

    th = pdf.font_size

    for row in result:
        pdf.cell(col_width, th, "ID")
        pdf.cell(col_width, th, "Status")
        pdf.cell(col_width*7, th, str(row.status))
        pdf.ln(th)
        pdf.cell(col_width, th, "From Address ")
        pdf.cell(col_width, th, str(row.from_address.address))
        pdf.cell(col_width, th, "To Address ")
        pdf.cell(col_width, th, str(row.to_address.address))
        pdf.cell(col_width, th, "Paid price ")
        pdf.cell(col_width, th, str(row.price))
        revenue+= row.price
        pdf.ln(th)
        pdf.cell(col_width, th, "==========================================================================")
        pdf.ln(th)
        pdf.ln(th)
    pdf.cell(col_width*2, th,"Company's revenue")
    pdf.cell(col_width*5, th, str(revenue))
    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=company_revenue_report.pdf'})


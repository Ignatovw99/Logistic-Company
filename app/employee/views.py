from flask import Blueprint, redirect, render_template, flash, request, url_for

from app.employee.forms import EmployeeForm, EmployeeUpdateForm

from app.auth.util import login_required, role_required, current_user
from app.common.util import persist_model, delete_model, commit_db_transaction, find_user_by_email
from app.employee.util import find_employee_by_id, find_all_active_shipments_by_employee
from app.office.util import find_office_by_id
from app.models import Employee, Role, User, Office


employee = Blueprint("employee", __name__)


@employee.route("/")
@login_required
@role_required(Role.EMPLOYEE)
def show():
    employees = Employee.query.all()
    return render_template("employee/all.html", employees=employees)


@employee.route("/create", methods=["GET", "POST"])
@login_required
@role_required(Role.ADMIN)
def create():
    form = EmployeeForm()
    form.office_id.choices = [(office.id, office.address) for office in Office.query.all()]

    if form.validate_on_submit():
        email = form.email.data

        if find_user_by_email(email):
            flash("Email already exists", "danger")
        else:
            email, first_name, last_name, address, phone_number, is_admin, is_courier, office_id, password = form.get_data()

            user = User(email=email, first_name=first_name, last_name=last_name, address=address, phone_number=phone_number, password=password)
            user.add_role(Role.CUSTOMER)
            user.add_role(Role.EMPLOYEE)

            if is_admin:
                user.add_role(Role.ADMIN)

            employee = Employee(user=user)

            if not is_courier:
                office = find_office_by_id(office_id)
                employee.office_id = office.id;
            
            persist_model(employee)
            flash("Employee created successfully", "success")
            return redirect(url_for("employee.show"))

    return render_template("employee/create.html", form=form)


@employee.route("/update/<id>", methods=["GET", "POST"])
@login_required
@role_required(Role.ADMIN)
def update(id):
    employee = find_employee_by_id(id)
    if not employee:
        flash("Employee does not exist", "danger")
        return redirect(url_for("employee.show"))

    form = EmployeeUpdateForm()
    form.office_id.choices = [(office.id, office.address) for office in Office.query.all()]

    if request.method == "GET":
        form.populate_form(employee)

    if form.validate_on_submit():
        email = form.email.data
        user_with_email = find_user_by_email(email)
        employee_user = employee.user

        if user_with_email and user_with_email.email != employee_user.email:
            flash("Email already exists", "danger")
        else:
            email, first_name, last_name, address, phone_number, is_admin, is_courier, office_id = form.get_data()
            employee_user.email = email
            employee_user.first_name = first_name
            employee_user.last_name = last_name
            employee_user.address = address
            employee_user.phone_number = phone_number

            if not is_admin and not employee_user.has_role(Role.ROOT):
                employee_user.remove_role(Role.ADMIN)
            if is_admin and not employee.user.has_role(Role.ADMIN):
                employee_user.add_role(Role.ADMIN)

            if is_courier:
                employee.office_id = None
            else:
                office = find_office_by_id(office_id)
                employee.office = office;
            
            commit_db_transaction()
            flash("Employee updated successfully", "success")
            return redirect(url_for("employee.show"))

    return render_template("employee/update.html", form=form, employee_id=employee.id)

        
@employee.route("/delete/<id>")
@login_required
@role_required(Role.ADMIN)
def delete(id):
    employee = find_employee_by_id(id)

    if not employee:
        flash("Employee does not exist", "danger")
    else:
        if current_user.id == employee.id:
            flash("You cannot delete yourself", "danger")
            return redirect(url_for("employee.show"))

        active_shipments = find_all_active_shipments_by_employee(employee)
        if active_shipments:
            flash("You cannot delete this employee because because he has to process some shipments", "warning")
        elif employee.user.has_role(Role.ROOT):
            flash("You are not allowed to delete the sys admin", "danger")
        else:
            #Deleting an employee don't remove the shipments related to this employee!
            user = employee.user
            delete_model(employee)
            delete_model(user)
            flash("Employee deleted successfully", "success")

    return redirect(url_for("employee.show"))

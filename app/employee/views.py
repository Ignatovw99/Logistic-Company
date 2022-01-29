from flask import Blueprint, redirect, render_template, flash, url_for

from app.employee.forms import EmployeeForm

from app.auth.util import login_required, role_required, current_user
from app.common.util import persist_model, delete_model, commit_db_transaction, find_user_by_email
from app.employee.util import find_employee_by_id, find_all_active_shipments_by_employee
from app.office.util import find_office_by_id
from app.models import Employee, Role, User


employee = Blueprint("employee", __name__)


@employee.route("/")
@login_required
@role_required(Role.EMPLOYEE)
def show():
    employees = Employee.query.all()
    # TODO show the highest role of each employee
    return render_template("employee/all.html", title="Employees", employees=employees)


@employee.route("/create")
@login_required
@role_required(Role.ADMIN)
def create():
    form = EmployeeForm()

    if form.validate_on_submit():
        email = form.email.data

        if find_user_by_email(email):
            flash("Email already exists")
        else:
            email, first_name, last_name, address, phone_number, is_admin, is_courier, office_id, password = form.get_data()

            user = User(email=email, first_name=first_name, last_name=last_name, address=address, phone_number=phone_number, password=password)
            user.add_role(Role.CLIENT)
            user.add_role(Role.EMPLOYEE)

            if is_admin:
                user.add_role(Role.ADMIN)

            employee = Employee(user=user)

            if not is_courier:
                office = find_office_by_id(office_id)
                employee.office_id = office.id;
            
            persist_model(employee)
            flash("Employee created successfully")
            return redirect(url_for("employee.show"))

    return render_template("employee/create.html", title="Employee create", form=form)


@employee.route("/update/<id>")
@login_required
@role_required(Role.ADMIN)
def update(id):
    employee = find_employee_by_id(id)
    if not employee:
        flash("Employee does not exist")
        return redirect(url_for("employee.show"))

    form = EmployeeForm()
    form.remove_password_required_validator()

    if form.validate_on_submit():
        email = form.email.data
        user_with_email = find_user_by_email(email)
        employee_user = employee.user

        if user_with_email and user_with_email.email != employee_user.email:
            flash("Email already exists")
            return render_template("employee/create.html", title="Employee update", form=form)
        else:
            email, first_name, last_name, address, phone_number, is_admin, is_courier, office_id, password = form.get_data()
            user = User(id=id, email=email, first_name=first_name, last_name=last_name, address=address, phone_number=phone_number)

            if password:
                user.password = password
            if not is_admin and not employee_user.has_role(Role.ROOT):
                user.remove_role(Role.ADMIN)

            employee = Employee(user=user)

            if is_courier:
                employee.office_id = None
            else:
                office = find_office_by_id(office_id)
                employee.office_id = office.id;
            
            commit_db_transaction()
            flash("Employee updated successfully")
            return redirect(url_for("employee.show"))

    form.populate_form(employee)
    return render_template("employee/create.html", title="Employee update", form=form)

        
@employee.route("/delete/<id>")
@login_required
@role_required(Role.ADMIN)
def delete(id):
    employee = find_employee_by_id(id)
    
    if current_user.id == employee.id:
        flash("You cannot delete yourself")
        return redirect(url_for("employee.show"))

    if employee:
        active_shipments = find_all_active_shipments_by_employee(employee)
        if active_shipments:
            flash("You cannot delete this employee because there are still some shipments to process")
        elif employee.user.has_role(Role.ROOT):
            flash("You are not allowed to delete the sys admin")
        else:
            delete_model(employee)
            flash("Employee deleted successfully")
    else:
        flash("Employee does not exist", "error")

    return redirect(url_for("employee.show"))

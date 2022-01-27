from flask import Blueprint, redirect, render_template, url_for, flash

from app.models import Office, Role
from app.auth.util import login_required, role_required
from app.common.util import commit_db_transaction, persist_model, delete_model
from app.office.forms import OfficeForm
from app.office.helper import find_office_by_id, is_address_available, find_all_active_shipments_by_office


office = Blueprint("office", __name__)


@office.route("/")
@login_required
@role_required(Role.EMPLOYEE)
def show():
    offices = Office.query.all()
    return render_template("office/all.html", title="Offices", offices=offices)


@office.route("/create", methods=["GET", "POST"])
@login_required
@role_required(Role.ADMIN)
def create():
    form = OfficeForm()
    
    if form.validate_on_submit():
        address = form.address.data

        if is_address_available(address):
            office = Office(address=address)
            persist_model(office)
            flash("Office created successfully")
            return redirect(url_for("office.show"))
        else:
            flash("There is already an office at this address")
        
    return render_template("office/create.html", title="Office create", form=form)


@office.route("/update/<id>", methods=["GET", "POST"])
@login_required
@role_required(Role.ADMIN)
def update(id):
    office = find_office_by_id(id)

    if not office:
        flash("Office does not exist")
        return redirect(url_for("office.show"))

    form = OfficeForm()

    if form.validate_on_submit():
        address = form.address.data
        if is_address_available(address):
            office.address = address
            commit_db_transaction(office)
            flash("Office updated successfully")
            return redirect(url_for("office.show"))
        else:
            flash("There is already an office at this address", "error")
            return render_template("office/update.html", title="Office update", form=form)

    form.address.data = office.address
    return render_template("office/update.html", title="Office update", form=form)


@office.route("/delete/<id>")
@login_required
@role_required(Role.ADMIN)
def delete(id):
    office = find_office_by_id(id)

    if office:
        #Deleting an office means that all employees who work in that office become couriers and all shipping addreses related to this office should be invaldiated.
        active_shippments = find_all_active_shipments_by_office(office)
        if active_shippments:
            flash("You cannot delete this office because there are still some shipments to process")
        else:
            delete_model(office)
            flash("Office deleted successfully")
    else:
        flash("Office does not exist")

    return redirect(url_for("office.show"))

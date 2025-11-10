from main import app, db
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from main.models import Employee
from main.forms import EmpForm, LoginForm, DeleteForm

import os, uuid
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif"}
DOC_EXTS = IMAGE_EXTS | {".pdf"}

def _save_upload(file_storage, allowed_exts, prefix):
    
    if not file_storage or not getattr(file_storage, "filename", ""):
        return None

    raw_name = secure_filename(file_storage.filename or "")
    if not raw_name:
        return None

    ext = os.path.splitext(raw_name)[1].lower()
    if ext not in allowed_exts:
        raise ValueError(f"Invalid file type: {ext}")

    unique_name = f"{prefix}_{uuid.uuid4().hex}{ext}"
    upload_abs = app.config.get("UPLOAD_DIR_ABS")
    os.makedirs(upload_abs, exist_ok=True)
    file_storage.save(os.path.join(upload_abs, unique_name))
    return unique_name


########  Login page ##########

@app.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_emp = Employee.query.filter_by(empid=form.empid.data).first()
        if attempted_emp and attempted_emp.check_password(form.password.data):
            login_user(attempted_emp)
            flash("You are logged in.", "success")
            return redirect(url_for("employee_profile", emp_id=attempted_emp.id))
        flash("Invalid Employee ID or Password.", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out!", "info")
    return redirect(url_for("login"))


####### register new employee ########

@app.route("/register", methods=["GET", "POST"])
def emp_register():
    form = EmpForm()
    if form.validate_on_submit():
        photo_filename = _save_upload(form.photo.data, IMAGE_EXTS, prefix="photo")
        emp10th = _save_upload(form.emp10th.data, DOC_EXTS, prefix="ms10")
        emp12th = _save_upload(form.emp12th.data, DOC_EXTS, prefix="ms12")
        empgrad = _save_upload(form.empgrad.data, DOC_EXTS, prefix="msgrad")

        emp = Employee(
            empname=form.empname.data.strip(),
            empid=form.empid.data.strip(),
            empemail=form.empemail.data.strip().lower(),
            empphone=form.empphone.data.strip(),
            emptype=form.emptype.data,
            empposi=form.empposi.data or None,
            empdep=form.empdep.data,
            empdesg=form.empdesg.data or None,
            joindate=form.joindate.data,
            empprob=form.empprob.data or None,
            empadd=form.empadd.data or None,
            empro=form.empro.data or None,
            photo=photo_filename,
            empadhar=form.empadhar.data.strip(),
            emppan=(form.emppan.data or "").strip().upper(),
            emp10th=emp10th,
            emp12th=emp12th,
            empgrad=empgrad,
            password=form.password1.data,
            is_admin=form.is_admin.data,
        )

        try:
            db.session.add(emp)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            for f in (photo_filename, emp10th, emp12th, empgrad):
                if f:
                    try:
                        os.remove(os.path.join(app.config["UPLOAD_DIR_ABS"], f))
                    except OSError:
                        pass
            flash("Duplicate data (ID/Email/Phone/Aadhaar/PAN). Please fix and try again.", "danger")
            return render_template("emp_register.html", form=form)

        login_user(emp)
        flash("Employee added successfully!", "success")
        return redirect(url_for("detail"))

    if form.errors:
        for errs in form.errors.values():
            for err in errs:
                flash(err, "danger")
    return render_template("emp_register.html", form=form)


####### Employee Details ########

@app.route("/employee_detail")
@login_required
def detail():
    employees = Employee.query.order_by(Employee.id.desc()).all()
    delete_form= DeleteForm()
    return render_template("detail.html", employees=employees, delete_form=delete_form)



####### Employee Profile #######

@app.route("/employee/<int:emp_id>")
@login_required
def employee_profile(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    return render_template("employee_profile.html", emp=emp)


######## Delete Employee  ########

@app.route("/employee/<int:emp_id>/delete", methods=["POST"])
@login_required
def delete_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    flash("Employee deleted successfully!", "info")
    return redirect(url_for("detail"))
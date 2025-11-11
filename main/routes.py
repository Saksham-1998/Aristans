from main import app, db
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from main.models import Employee, Attendance, AttendanceStatus, Rating
from main.forms import EmpForm, LoginForm, DeleteForm, RatingForm, AttendanceMonthForm

import os, uuid
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import date

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

# ---------- Auth ----------
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

# ---------- Register ----------
@app.route("/register", methods=["GET", "POST"])
def emp_register():
    form = EmpForm()
    if form.validate_on_submit():
        photo_filename = _save_upload(form.photo.data, IMAGE_EXTS, prefix="photo")
        emp10th = _save_upload(form.emp10th.data, DOC_EXTS, prefix="ms10")
        emp12th = _save_upload(form.emp12th.data, DOC_EXTS, prefix="ms12")
        empgrad = _save_upload(form.empgrad.data, DOC_EXTS, prefix="msgrad")

        emp = Employee(
            empname=form.empname.data,
            empid=form.empid.data,
            empemail=form.empemail.data.lower(),
            empphone=form.empphone.data,
            emptype=form.emptype.data,
            empposi=form.empposi.data,
            empdep=form.empdep.data,
            empdesg=form.empdesg.data,
            joindate=form.joindate.data,
            empprob=form.empprob.data,
            empadd=form.empadd.data,
            empro=form.empro.data,
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



# ----- Employee list (detail) -----
@app.route("/employee_detail")
@login_required
def detail():
    employees = Employee.query.order_by(Employee.id.desc()).all()
    delete_form = DeleteForm()
    form = RatingForm()

    today = date.today()
    form.year.data = today.year
    form.month.data = str(today.month)

    return render_template(
        "detail.html",
        employees=employees,
        form=form,
        delete_form=delete_form,
        current_year=today.year,)


# ----- Save/update a MONTHLY rating -----
@app.route("/employee/<int:emp_id>/rate", methods=["POST"])
@login_required
def rate_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    form = RatingForm()
    if not form.validate_on_submit():
        flash("Invalid rating submission.", "danger")
        return redirect(url_for("detail"))

    year = int(form.year.data)
    month = int(form.month.data)
    score = int(form.score.data)

    # upsert
    rec = Rating.query.filter_by(employee_id=emp.id, year=year, month=month).first()
    if rec:
        rec.score = score
        msg = "Rating updated."
    else:
        db.session.add(Rating(employee_id=emp.id, year=year, month=month, score=score))
        msg = "Rating saved."

    try:
        db.session.commit()
        flash(f"{msg} ({emp.empname} — {month:02d}/{year}: {score}★).", "success")
    except IntegrityError:
        db.session.rollback()
        flash("A rating for that month already exists.", "warning")

    return redirect(url_for("detail"))



# ----- Employee profile: monthly ratings history + average -----
@app.route("/employee/<int:emp_id>")
@login_required
def employee_profile(emp_id):
    emp = Employee.query.get_or_404(emp_id)

    # Monthly ratings history (newest first)
    monthly_ratings = (Rating.query
                       .filter_by(employee_id=emp.id)
                       .order_by(Rating.year.desc(), Rating.month.desc())
                       .all())

    # Average across all months
    avg_val = db.session.query(func.avg(Rating.score)).filter(Rating.employee_id == emp.id).scalar()
    average_rating = float(avg_val) if avg_val is not None else None

    # Attendance view (optional): last 12 months, newest first
    recent_att = (Attendance.query
                  .filter_by(employee_id=emp.id)
                  .order_by(Attendance.year.desc(), Attendance.month.desc())
                  .limit(12).all())

    return render_template("employee_profile.html",
                           emp=emp,
                           monthly_ratings=monthly_ratings,
                           average_rating=average_rating,
                           recent_att=recent_att)



# ---------- Attendance manage ----------
@app.route("/employee/<int:emp_id>/attendance/manage", methods=["GET", "POST"])
@login_required
def manage_attendance(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    aform = AttendanceMonthForm()

    if request.method == "GET":
        t = date.today()
        aform.year.data = t.year
        aform.month.data = str(t.month)

    if aform.validate_on_submit():
        year = int(aform.year.data)
        month = int(aform.month.data)
        status = AttendanceStatus(aform.status.data)
        notes = aform.notes.data or None

        rec = Attendance.query.filter_by(employee_id=emp.id, year=year, month=month).first()
        if rec:
            rec.status = status
            rec.notes = notes
            action = "updated"
        else:
            rec = Attendance(employee_id=emp.id, year=year, month=month, status=status, notes=notes)
            db.session.add(rec)
            action = "saved"

        try:
            db.session.commit()
            flash(f"Attendance {action} for {emp.empname} — {month:02d}/{year}.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Attendance for that month already exists.", "warning")

        return redirect(url_for("manage_attendance", emp_id=emp.id))

    recent = (Attendance.query
              .filter_by(employee_id=emp.id)
              .order_by(Attendance.year.desc(), Attendance.month.desc())
              .limit(24).all())

    return render_template("manage_attendance.html", emp=emp, aform=aform, recent=recent)



# ---------- Delete employee ----------
@app.route("/employee/<int:emp_id>/delete", methods=["POST"])
@login_required
def delete_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    # Validate CSRF with DeleteForm (optional but good)
    form = DeleteForm()
    if not form.validate_on_submit():
        flash("Invalid delete request.", "danger")
        return redirect(url_for("detail"))

    db.session.delete(emp)
    db.session.commit()
    flash("Employee deleted successfully!", "info")
    return redirect(url_for("detail"))
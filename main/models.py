# main/models.py
from main import db, bcrypt
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import event
from pathlib import Path
from flask import current_app
from enum import Enum

class Employee(db.Model, UserMixin):
    __tablename__= "employee"
    id = db.Column(db.Integer, primary_key=True)
    empname = db.Column(db.String(50), nullable=False)
    empid = db.Column(db.String(50), nullable=False, unique=True)
    empemail = db.Column(db.String(100), nullable=False)
    empphone = db.Column(db.String(10), nullable=False, unique=True)
    emptype = db.Column(db.String(50), nullable=False)
    empposi = db.Column(db.String(100), nullable=True)
    empdep  = db.Column(db.String(100), nullable=True)
    empdesg = db.Column(db.String(100), nullable=True)
    joindate= db.Column(db.DateTime, default=datetime.utcnow)
    empprob = db.Column(db.String(100), nullable=True)
    empadd  = db.Column(db.Text, nullable=True)
    empro   = db.Column(db.String(50), nullable=True)
    empadhar= db.Column(db.String(12), nullable=True, unique=True)
    emppan  = db.Column(db.String(10), nullable=True, unique=True)
    photo   = db.Column(db.String(200), nullable=True)
    emp10th = db.Column(db.String(200), nullable=True)
    emp12th = db.Column(db.String(200), nullable=True)
    empgrad = db.Column(db.String(200), nullable=True)
    password_hash = db.Column(db.String(100), nullable=False)
    is_admin= db.Column(db.Boolean, default=False)

    # relationships
    ratings = db.relationship("Rating", backref="employee", lazy="dynamic", cascade="all, delete-orphan")

    attendances = db.relationship("Attendance", backref="employee", lazy="dynamic", cascade="all, delete-orphan")

    # helpers for ratings
    def month_rating(self, year: int, month: int):
        return self.ratings.filter_by(year=year, month=month).first()

    @property
    def average_rating(self):
        val = self.ratings.with_entities(db.func.avg(Rating.score)).scalar()
        return float(val) if val is not None else None

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"The name of the user is {self.empname}"


# ---- Monthly Rating (one per employee per month) ----
class Rating(db.Model):
    __tablename__ = "rating"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id", ondelete="CASCADE"), nullable=False)
    year  = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1..12
    score = db.Column(db.SmallInteger, nullable=False)  # 1..5

    __table_args__ = (
        db.UniqueConstraint("employee_id", "year", "month", name="uq_employee_year_month"),
        db.CheckConstraint("score BETWEEN 1 AND 5", name="ck_score_1_5"),
        db.CheckConstraint("month BETWEEN 1 AND 12", name="ck_month_1_12"),
    )


# ----- Attendance (your existing monthly model) -----
class AttendanceStatus(Enum):
    PRESENT = "Present"
    ABSENT  = "Absent"
    LEAVE   = "Leave"
    WFH     = "WFH"
    MIXED   = "Mixed"

class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)
    notes = db.Column(db.String(300))
    __table_args__ = (db.UniqueConstraint("employee_id", "year", "month", name="uq_att_employee_year_month"),)


# ---- auto-delete uploaded files on Employee row removal ----
def _delete_from_model(filename: str):
    if not filename:
        return
    try:
        upload_abs = Path(current_app.config['UPLOAD_DIR_ABS']).resolve()
        path = (upload_abs / filename).resolve()
        if not str(path).startswith(str(upload_abs)):
            current_app.logger.warning(f"Blocked deletion outside upload dir: {path}")
            return
        if path.is_file():
            path.unlink(missing_ok=True)
    except Exception as e:
        current_app.logger.warning(f"Could not delete file {filename}: {e}")

@event.listens_for(Employee, "after_delete")
def employee_files_after_delete(mapper, connection, target):
    for attr in ("photo", "emp10th", "emp12th", "empgrad"):
        val = getattr(target, attr, None)
        if val:
            _delete_from_model(val)
from main import db , bcrypt
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import event
from pathlib import Path
from flask import current_app



class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key = True)
    empname= db.Column(db.String(length=50),nullable= False)
    empid= db.Column(db.String(length=50),nullable=False, unique= True)
    empemail= db.Column(db.String(length=100), nullable= False)
    empphone= db.Column(db.String(10), nullable = False, unique=True)
    emptype = db.Column(db.String(50), nullable=False)
    empposi = db.Column(db.String(100), nullable=True)
    empdep= db.Column(db.String(length=100),nullable= True)
    empdesg= db.Column(db.String(length=100),nullable=True)
    joindate= db.Column(db.DateTime, default= datetime.utcnow)
    empprob= db.Column(db.String(length=100),nullable= True)
    empadd= db.Column(db.Text,nullable=True)
    empro= db.Column(db.String(length=50),nullable=True)
    empadhar = db.Column(db.String(12), nullable=True, unique=True)
    emppan = db.Column(db.String(10), nullable=True, unique=True)
    photo = db.Column(db.String(200), nullable=True)
    emp10th = db.Column(db.String(200), nullable=True)
    emp12th = db.Column(db.String(200), nullable=True)
    empgrad = db.Column(db.String(200), nullable=True)
    password_hash= db.Column(db.String(length=100), nullable=False)
    is_admin= db.Column(db.Boolean, default=False)

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
    

    
def _delete_from_model(filename: str):

    if not filename:
        return
    try:
        upload_abs = Path(current_app.config['UPLOAD_DIR_ABS']).resolve()
        path = (upload_abs / filename).resolve()

        # Safety: only delete inside the upload folder
        if not str(path).startswith(str(upload_abs)):
            current_app.logger.warning(f"Blocked deletion outside upload dir: {path}")
            return

        if path.is_file():
            path.unlink(missing_ok=True)
            current_app.logger.info(f"Deleted file (event): {path}")
        else:
            current_app.logger.info(f"File not found (event): {path}")
    except Exception as e:
        current_app.logger.warning(f"Could not delete file {filename}: {e}")

@event.listens_for(Employee, "after_delete")
def employee_files_after_delete(mapper, connection, target):
    """Auto-delete uploaded files when an Employee row is removed."""
    for attr in ("photo", "emp10th", "emp12th", "empgrad"):
        val = getattr(target, attr, None)
        if val:
            _delete_from_model(val)
from main import db , bcrypt
from flask_login import UserMixin
from datetime import datetime


class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key = True)
    empname= db.Column(db.String(length=50),nullable= False)
    empid= db.Column(db.String(length=50),nullable=False, unique= True)
    empemail= db.Column(db.String(length=100), nullable= False)
    empphone= db.Column(db.String(10), nullable = False, unique=True)
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
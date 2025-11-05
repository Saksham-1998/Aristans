from flask_login import UserMixin
from main import db


class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key = True)
    empname= db.Column(db.String(length=50),nullable= False)
    empid= db.Column(db.String(length=50),nullable=False, unique= True)
    password_hash= db.Column(db.String(length=100), nullable=False)

    def __repr__(self):
        return f"The name of the user is {self.empname}"
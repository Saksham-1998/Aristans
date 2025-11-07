from flask_login import UserMixin
from main import db , bcrypt


class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key = True)
    empname= db.Column(db.String(length=50),nullable= False)
    empid= db.Column(db.String(length=50),nullable=False, unique= True)
    empemail= db.Column(db.String(length=100), nullable= False)
    password_hash= db.Column(db.String(length=100), nullable=False)

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
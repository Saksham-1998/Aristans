from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Length, EqualTo, Email

from main.models import Employee


class EmpForm(FlaskForm):
    empname= StringField(label="Employee name: ", validators= [DataRequired(), Length(min=2,max=30)])
    empid= StringField(label="Employee Id: ", validators= [DataRequired(), Length(min=2,max=30)])
    empemail= StringField(label="Employee Email: ", validators=[Email(), DataRequired()])    
    password1= PasswordField(label="Create Password: ", validators=[DataRequired(), Length(min=6)] )
    password2= PasswordField(label="Type Password Again: ", validators=[DataRequired(), EqualTo('password1', message="password didn't match")])
    submit= SubmitField(label="Create Account") 

    def validate_empid(self, empid_to_check):
        emp= Employee.query.filter_by(empid= empid_to_check.data).first()
        if emp:
            raise ValidationError("Employee Id already exist")
        

class LoginForm(FlaskForm):
    empid = StringField(label="Enter Employee ID:", validators=[DataRequired()])
    password = PasswordField(label="Enter Password", validators=[DataRequired()])
    submit = SubmitField(label="Sign in")
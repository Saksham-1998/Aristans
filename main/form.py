from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length, EqualTo, Email, Optional

from main.models import Employee


class EmpForm(FlaskForm):
    empname= StringField("Employee name: ", validators= [DataRequired(), Length(min=2,max=30)])
    empid= StringField("Employee Id: ", validators= [DataRequired(), Length(min=2,max=30)])
    empemail= StringField("Employee Email: ", validators=[Email(), DataRequired()])
    empdep= SelectField('Department',
                        choices=[
                            ('','Select Department'),
                            ('HR','Human Resource'),
                            ('Tech','Technology'),
                            ('Sales','Sales'),
                            ('Finance','Finance'),
                            ('Marketing','Marketing'),
                            ('Creative','Creative'),
                            ('Operations','Operations'),
                            ], validators=[DataRequired()])
    empdesg= StringField("Employee Designation:", validators=[Length(max=100),Optional()])
    joindate= DateField('Date Joined', format="%d-%m-%Y", validators=[Optional()])
    empadd= TextAreaField('Address', validators=[Optional()])
    empro= StringField('Reporting Officer', validators=[Optional()])
    password1= PasswordField(label="Create Password: ", validators=[DataRequired(), Length(min=6)] )
    password2= PasswordField(label="Type Password Again: ", validators=[DataRequired(), EqualTo('password1', message="password didn't match")])
    is_admin= BooleanField('Is Admin?')
    submit= SubmitField(label="Save") 

    def validate_empid(self, empid_to_check):
        emp= Employee.query.filter_by(empid= empid_to_check.data).first()
        if emp:
            raise ValidationError("Employee Id already exist")
        

class LoginForm(FlaskForm):
    empid = StringField(label="Enter Employee ID:", validators=[DataRequired()])
    password = PasswordField(label="Enter Password", validators=[DataRequired()])
    submit = SubmitField(label="Sign in")
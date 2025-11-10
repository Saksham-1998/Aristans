from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, DateField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length, EqualTo, Email, Optional

from main.models import Employee


class EmpForm(FlaskForm):
    empname= StringField("Enter Full Name : ", validators= [DataRequired(), Length(min=2,max=30)])
    empid= StringField("Employee ID : ", validators= [DataRequired(), Length(min=2,max=30)])
    empemail= StringField("Email : ", validators=[Email(), DataRequired()])
    empphone= StringField("Phone Number :", validators=[DataRequired(), Length(min=10, max=10, message="Enter a 10 digit Number!")])
    emptype= SelectField("Type of Employement :",
                        choices=[
                            ('',"Select Employement Type"),
                            ('Full-time',"Full-time"),
                            ('Part-time',"Part-time"),
                            ('Intern/Trainee',"Intern/Trainee"),
                            ('Consultant',"Consultant"),
                            ('Temporary',"Temporary"),
                            ('Others',"Others"),
                         ], validators=[DataRequired(message="please select employement type!")])
    empposi= StringField("Position :", validators=[Optional(),Length(max=100)])
    empdep= SelectField('Department :',
                        choices=[
                            ('','Select Department'),
                            ('HR','Human Resource'),
                            ('Tech Team','Technology'),
                            ('Sales Team','Sales'),
                            ('Finance','Finance'),
                            ('Marketing','Marketing'),
                            ('Creative','Creative'),
                            ('Operations','Operations'),
                            ('Store Managers/Operators',"Store Managers/Operators"),
                            ], validators=[DataRequired(message="Please select a department!")])
    empdesg= StringField("Designation :", validators=[Length(max=100),Optional()])
    joindate= DateField('Date of Joining :', format="%Y-%m-%d", validators=[Optional()])
    empprob= StringField('Probation Period :',validators=[Optional()])
    empadd= TextAreaField('Address :', validators=[Optional()])
    empadhar = StringField('Aadhar Card No.:', validators=[DataRequired(), Length(min=12, max=12, message="Aadhar must be 12 digits!")])
    emppan = StringField('PAN Card :', validators=[DataRequired(), Length(min=10, max=10, message="PAN must be 10 characters!")])
    empro= StringField('Reporting Officer :', validators=[Optional()])
    photo = FileField('Profile Photo :', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    emp10th = FileField("10th Marksheet :", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif", "pdf"], "Images/PDF only")])
    emp12th = FileField("12th Marksheet :", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif", "pdf"], "Images/PDF only")])
    empgrad = FileField("Graduation Marksheet :", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif", "pdf"], "Images/PDF only")])
    password1= PasswordField(label="Create Password : ", validators=[DataRequired(), Length(min=6)] )
    password2= PasswordField(label="", validators=[DataRequired(), EqualTo('password1', message="password didn't match")])
    is_admin= BooleanField('is Admin?')
    submit= SubmitField(label="Save") 

    def validate_empid(self, empid_to_check):
        emp= Employee.query.filter_by(empid= empid_to_check.data).first()
        if emp:
            raise ValidationError("Employee Id already exist")
        

class LoginForm(FlaskForm):
    empid = StringField(label="Enter Employee ID:", validators=[DataRequired()])
    password = PasswordField(label="Enter Password", validators=[DataRequired()])
    submit = SubmitField(label="Sign in")

class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")
    
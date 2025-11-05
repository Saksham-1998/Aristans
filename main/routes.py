from main import app

from flask_login import login_user, logout_user, login_required

from flask import render_template, redirect, url_for, flash, session, Response

from main.models import Employee
from main.form import EmpForm, LoginForm
from main import db


### Login User ###
@app.route("/", methods = ['Get', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form = form)

### Employee Detail ###
@login_required
@app.route("/employee_detail")
def detail():
    return render_template('detail.html')

### MY ID Detail ###
@login_required
@app.route("/my_id")
def my_id():
    return render_template('myid.html')
    


### register new employee (HR only) ###
@app.route("/register", methods= ['GET','POST'])
def emp_register():
    form = EmpForm()
    if form.validate_on_submit():
        emp_to_create = Employee(empname= form.empname.data,
                                 empid= form.empid.data,
                                 password_hash= form.password1.data)
        
        db.session.add(emp_to_create)
        db.session.commit()

        return redirect(url_for('my_id'))



    return render_template('emp_register.html', form = form)


## Logout User ##
@app.route('/logout')
@login_required
def logout():
    flash("You have logged Out!", category="info")
    return redirect(url_for('login.html'))

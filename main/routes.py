from main import app , db
from flask import render_template, redirect, url_for, flash, session, Response

from flask_login import login_user, logout_user, login_required

from main.models import Employee
from main.form import EmpForm, LoginForm


### Login User ###
@app.route("/", methods = ['Get', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_emp = Employee.query.filter_by(empid=form.empid.data).first()
        if attempted_emp and attempted_emp.check_password(form.password.data):
            login_user(attempted_emp)
            flash(f'You are logged_in', category='success')
            return redirect(url_for('my_id'))
        else:
            flash('Invalid Employee ID and Password', category='danger')

    return render_template('login.html', form = form)

### Employee Detail ###

@app.route("/employee_detail")
@login_required
def detail():
    return render_template('detail.html')

### MY ID Detail ###

@app.route("/my_id")
@login_required
def my_id():
    return render_template('myid.html')
    


### register new employee (HR only) ###

@app.route("/register", methods= ['GET','POST'])
def emp_register():
    form = EmpForm()
    if form.validate_on_submit():
        emp = Employee(empname= form.empname.data,
                                 empid= form.empid.data,
                                 password= form.password1.data)
        
        db.session.add(emp)
        db.session.commit()
        login_user(emp)
        flash('Account created successfully! You are LoggedIn ', category='success')
        return redirect(url_for('detail'))
    
    if form.errors != {}: ##checking error from validation
        for err_msg in form.errors.values():
            flash(f'{err_msg}', category='danger')

    return render_template('emp_register.html', form = form)


## Logout User ##
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged Out!", category="info")
    return redirect(url_for('login'))
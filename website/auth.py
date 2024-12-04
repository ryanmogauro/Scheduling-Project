from flask import Blueprint, render_template, redirect, url_for
from flask import request, request, flash
from website.models import User, Employee, Unavailability, Shift, ShiftAssignment
from flask_login import login_user, logout_user, login_required, current_user
from website import db
from .models import User

# Create a blueprint
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.schedule'))
        
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()

        if user:
            login_user(user, remember=remember)
            return redirect(url_for('main.schedule'))

        if not user:
            flash("We couldn't find an account with that email address.", "danger")
        else:
            flash("The password you entered is incorrect.", "danger")
        
    return render_template('signin.html')




@auth_blueprint.route('/', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.schedule'))

    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')

        if not firstName or not lastName:
            flash("First name and last name are required.")
            return redirect(url_for('auth.signup'))

        if not email.endswith('@colby.edu'):
            flash("Email must be from the domain @colby.edu.")
            return redirect(url_for('auth.signup'))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with that email already exists.")
            return redirect(url_for('auth.signup'))
        
        if len(password) > 20 or len(password) < 5: 
            flash("Password must be between 5 and 20 characters.")
            return redirect(url_for('auth.signup'))
        
        new_employee = Employee(
            firstName = firstName, 
            lastName = lastName, 
            minHours = 4,
            maxHours = 12, 
            )
        
        db.session.add(new_employee)
        db.session.commit()
        
        new_employeeID = new_employee.employeeID
        new_user = User(
            employeeID = new_employeeID,
            email = email
            )
        
        new_user.set_password(password)
        db.session.add(new_user)
        try:
            db.session.commit()
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback() 
            flash("Error creating user: " + str(e))
            return redirect(url_for('auth.signup'))
    
    return render_template('signup.html')



@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))



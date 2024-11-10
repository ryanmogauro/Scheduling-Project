from flask import Blueprint, render_template, redirect, url_for
from flask import request, request, flash
from models import db, User, Employee, Unavailability, Shift, ShiftAssignment
from flask_login import login_user, logout_user, login_required, current_user

# Create a blueprint
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.schedule'))

        if not user:
            flash("No existing user with provided email")
        else:
            flash("Incorrect Password")
        
    
    return render_template('signin.html')




@auth_blueprint.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with that email already exists. Please log in.")
            return redirect(url_for('auth.login'))
        
        if len(password) > 20 or len(password) < 5: 
            flash("Password must be between 5 and 20 characters")
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



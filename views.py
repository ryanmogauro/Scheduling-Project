from flask import Blueprint, render_template, redirect, url_for
from flask import request
from models import db, User, Employee, Unavailability, Shift, ShiftAssignment
from flask_login import login_required, current_user
from datetime import datetime, timedelta

# Create a blueprint
main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    if request.method == 'POST':
        #logic for admin writing a new schedule
        pass
    
    weekStartDay, weekEndDay = getWeekBounds(datetime.now()) #will need to change datetime.now for viewing different weeks
    
    shifts = Shift.query.filter(Shift.shiftStartTime.between(weekStartDay, weekEndDay)).all()
    
    return render_template('schedule.html', shifts=shifts) #need to make schedule.html interface



#maybe make a method for route /myschedule too

    
def getWeekBounds(date):
     # Calculate date of Monday date week
    start_of_week = date - timedelta(days=(date.weekday()))
    
    # Calculate date of Sunday of date week
    end_of_week = start_of_week + timedelta(days=6)
    
    return start_of_week, end_of_week

@main_blueprint.route('/unavailability', methods=['GET', 'POST'])
@login_required
def unavailability():
    if request.method == 'POST':
        #logic to add/update unavailability preferences
        pass
    
    currentUnavailability = Unavailability.filter_by(employeeID = current_user.employeeID).all()
    
    return render_template('unavailability.html', unavailability = currentUnavailability)









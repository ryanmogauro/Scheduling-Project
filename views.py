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
        schedule = None #get all new shifts from front-end
        
        for shift in schedule:
            new_shift = Shift(
                shiftStartTime = shift.start, 
                shiftEndTime = shift.end
            )
            
            new_shift_id = new_shift.shiftID
            new_shift_assignment = ShiftAssignment(
                shiftID = new_shift_id, 
                employee = current_user.get_id()
            )
            
        
    
    weekStartDay, weekEndDay = getWeekBounds(datetime.now()) #will need to change datetime.now for viewing different weeks
    
    shifts = Shift.query.filter(Shift.shiftStartTime.between(weekStartDay, weekEndDay)).all()
    
    employee = Employee.query.filter(Employee.employeeID == current_user.employeeID).first()
    
    name = employee.firstName if employee else None
    
    
    return render_template('schedule.html', shifts=shifts, name = name) #need to make schedule.html interface



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
       
        startTime = datetime.strptime(request.form['start-time-input'],'%Y-%m-%dT%H:%M')
        endTime = datetime.strptime(request.form['end-time-input'],'%Y-%m-%dT%H:%M')
        new_unavailable_span = Unavailability(
                employeeID = current_user.employeeID,
                unavailableStartTime = startTime, 
                unavailableEndTime = endTime
            )
            
            #add new unavailable span to db
        db.session.add(new_unavailable_span)
        db.session.commit(); 
            
        
         
        
    #currentUnavailability = Unavailability.filter_by(employeeID = current_user.employeeID).all()
    
    return render_template('unavailability.html', unavailability = None)









from flask import Blueprint, render_template, redirect, url_for
from flask import request, jsonify
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
    
    #shifts = Shift.query.filter(Shift.shiftStartTime.between(weekStartDay, weekEndDay)).all()
    
    employee = Employee.query.filter(Employee.employeeID == current_user.employeeID).first()
    
    name = employee.firstName if employee else None
    
    shifts = [
        {"day": "Monday", "start_hour": 9, "end_hour": 13},
        {"day": "Wednesday", "start_hour": 11, "end_hour": 15}
    ] 
    
    """ shiftAssignments = ShiftAssignment.query.filter(ShiftAssignment.employeeID == current_user.employeeID).first()
    
    shifts = Shift.query.filter(Shift.shiftID in shiftAssignments)
    
     """
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
    
    #standardize day of week to date
    #have to do this because used DATETIME instead of TIME
    
    dateToDay = {
        'Monday' : datetime(2001, 1,1),
        'Tuesday' : datetime(2001, 1, 2),
        'Wednesday' : datetime(2001, 1, 3),
        'Thursday' : datetime(2001, 1, 4),
        'Friday' : datetime(2001, 1, 5),
        'Saturday' : datetime(2001, 1, 6),
        'Sunday' : datetime(2001, 1, 7),
    }
    
    if request.method == 'POST':
        
        unavailabilityJSON = request.get_json()
        unavailability = unavailabilityJSON['slots']
        
        if unavailability:
            prior_unavailability = Unavailability.query.filter(Unavailability.employeeID == current_user.employeeID).all()
            for entry in prior_unavailability:
                db.session.delete(entry)
            db.session.commit()

        #response currently sends day of week instead of date
        #will need to figure this out on front-end
        for slot in unavailability: 
            day = slot['day']
            day_date = dateToDay[day]
            start_time = datetime.combine(day_date, datetime.strptime(slot["startTime"], "%H:%M").time())
            end_time = datetime.combine(day_date, datetime.strptime(slot["endTime"], "%H:%M").time())

            new_unavailable_slot = Unavailability(
                employeeID = current_user.employeeID, 
                unavailableStartTime = start_time, 
                unavailableEndTime = end_time
            )
            print("About to add this object to unavailability! at: " + str(new_unavailable_slot.unavailableStartTime))
            db.session.add(new_unavailable_slot)
            db.session.commit(); 
        
         
    #still need
    current_unavailability = Unavailability.query.filter(Unavailability.employeeID == current_user.employeeID).all()
    print(str(current_user.email) + " is unavail : " + str([slot.unavailableStartTime for slot in current_unavailability]))
    unavailability_list = [
        {
            "day": entry.unavailableStartTime.strftime('%A'),  # Get the day name (e.g., Monday)
            "startTime": entry.unavailableStartTime.strftime('%H:%M'),
            "endTime": entry.unavailableEndTime.strftime('%H:%M')
        } for entry in current_unavailability
    ]
    
    return render_template('unavailability.html', unavailability = unavailability_list)

@main_blueprint.route('/get_unavailability', methods=['GET', 'POST'])
@login_required
def get_availability(): 
    print("getting unavail")

    current_unavailability = Unavailability.query.filter(Unavailability.employeeID == current_user.employeeID).all()
    
    unavailability_list = [
        {
            "day": entry.unavailableStartTime.strftime('%A'),  # Day name (e.g., Monday)
            "startTime": entry.unavailableStartTime.strftime('%H:%M'),
            "endTime": entry.unavailableEndTime.strftime('%H:%M')
        } for entry in current_unavailability
    ]
    
    print("Fetching availability for " + str(current_user.email) + " : " + str(unavailability_list))
    
    curr_employee = Employee.query.where(Employee.employeeID == current_user.employeeID).first()
    return jsonify({'availability': unavailability_list, 'name': curr_employee.firstName})


@main_blueprint.route('/add_availability', methods=['POST'])
@login_required
def add_availability():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    day = data.get('day')
    start_time_str = data.get('startTime')
    end_time_str = data.get('endTime')

    if not all([day, start_time_str, end_time_str]):
        return jsonify({'success': False, 'error': 'Missing data fields'}), 400

    dateToDay = {
        'Monday': datetime(2001, 1, 1),
        'Tuesday': datetime(2001, 1, 2),
        'Wednesday': datetime(2001, 1, 3),
        'Thursday': datetime(2001, 1, 4),
        'Friday': datetime(2001, 1, 5),
        'Saturday': datetime(2001, 1, 6),
        'Sunday': datetime(2001, 1, 7),
    }

    try:
        day_date = dateToDay[day]
        start_time = datetime.combine(day_date, datetime.strptime(start_time_str, "%H:%M").time())
        end_time = datetime.combine(day_date, datetime.strptime(end_time_str, "%H:%M").time())

        new_unavailable_slot = Unavailability(
            employeeID=current_user.employeeID,
            unavailableStartTime=start_time,
            unavailableEndTime=end_time
        )
        db.session.add(new_unavailable_slot)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error adding availability: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500
    

@main_blueprint.route('/delete_availability', methods=['POST'])
@login_required
def delete_availability():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    day = data.get('day')
    start_time_str = data.get('startTime')
    end_time_str = data.get('endTime')

    if not all([day, start_time_str, end_time_str]):
        return jsonify({'success': False, 'error': 'Missing data fields'}), 400

    dateToDay = {
        'Monday': datetime(2001, 1, 1),
        'Tuesday': datetime(2001, 1, 2),
        'Wednesday': datetime(2001, 1, 3),
        'Thursday': datetime(2001, 1, 4),
        'Friday': datetime(2001, 1, 5),
        'Saturday': datetime(2001, 1, 6),
        'Sunday': datetime(2001, 1, 7),
    }

    try:
        day_date = dateToDay[day]
        start_time = datetime.combine(day_date, datetime.strptime(start_time_str, "%H:%M").time())
        end_time = datetime.combine(day_date, datetime.strptime(end_time_str, "%H:%M").time())

        # Find the unavailability slot to delete
        slot_to_delete = Unavailability.query.filter_by(
            employeeID=current_user.employeeID,
            unavailableStartTime=start_time,
            unavailableEndTime=end_time
        ).first()

        if slot_to_delete:
            db.session.delete(slot_to_delete)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Slot not found'}), 404
    except Exception as e:
        print(f"Error deleting availability: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/unavailability', methods=['GET'])
@login_required
def unavailability_page():
    return render_template('unavailability.html')
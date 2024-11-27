from flask import Blueprint, render_template, redirect, url_for
from flask import request, jsonify
from website.models import User, Employee, Unavailability, Shift, ShiftAssignment
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from website import db
from website.scheduleGenerator import getEmployees, getAvailabilityDict, generateSchedule

# Create a blueprint
main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/schedule', methods=['GET'])
@login_required
def schedule():
    curr_employee = Employee.query.where(Employee.employeeID == current_user.employeeID).first()
    return render_template('schedule.html', fname=curr_employee.firstName, lname=curr_employee.lastName)

@main_blueprint.route('/get_schedule', methods=['POST'])
@login_required
def get_schedule():
    # Get the week input from the form -- ISO Format!
    schedule_date = request.form.get('scheduleDate')
    year, week = map(int, schedule_date.split('-W'))
    week_start_date = datetime.strptime(f'{year} {week} 1', '%G %V %u')
    print(week_start_date)
    week_end_date = week_start_date + timedelta(days=6)

    print(f"Week Start: {week_start_date}, Week End: {week_end_date}")

    shifts_for_week = (
        db.session.query(Shift)
        .join(ShiftAssignment, Shift.shiftID == ShiftAssignment.shiftID)
        .filter(ShiftAssignment.employeeID == current_user.employeeID)
        .filter(Shift.shiftStartTime >= week_start_date, Shift.shiftEndTime <= week_end_date)
        .all()
    )
    
    return jsonify({
        "shifts": [
            {"shiftID": shift.shiftID, "start": shift.shiftStartTime.isoformat(), "end": shift.shiftEndTime.isoformat()}
            for shift in shifts_for_week
        ]
    })

def getWeekBounds(date):
    start_of_week = date - timedelta(days=(date.weekday()))
    
    end_of_week = start_of_week + timedelta(days=6)
    
    return start_of_week, end_of_week

@main_blueprint.route('/unavailability', methods=['GET', 'POST'])
@login_required
def unavailability():
    
    
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
        
    current_unavailability = Unavailability.query.filter(Unavailability.employeeID == current_user.employeeID).all()
    unavailability_list = [
        {
            "day": entry.unavailableStartTime.strftime('%A'),
            "startTime": entry.unavailableStartTime.strftime('%H:%M'),
            "endTime": entry.unavailableEndTime.strftime('%H:%M')
        } for entry in current_unavailability
    ]
    curr_employee = Employee.query.where(Employee.employeeID == current_user.employeeID).first()
    return render_template('unavailability.html', unavailability = unavailability_list, fname=curr_employee.firstName, lname=curr_employee.lastName)


@main_blueprint.route('/get_unavailability', methods=['POST'])
@login_required
def get_availability(): 
    data = request.get_json()
    strStartOfWeek = data.get('startOfWeek')
    
    try: 
        startOfWeek = datetime.strptime(strStartOfWeek.split("T")[0], '%Y-%m-%d').date() 

        startOfWeek, endOfWeek = getWeekBounds(startOfWeek)
        startOfWeekDatetime = datetime.combine(startOfWeek, datetime.min.time())
        endOfWeekDateTime = datetime.combine(endOfWeek, datetime.max.time())
        
        if not startOfWeek or not endOfWeek:
            return jsonify({'success': False, 'error': 'Missing year or week parameter'}), 400


        week_unavailability = Unavailability.query.filter(
            Unavailability.employeeID == current_user.employeeID,
            Unavailability.unavailableStartTime.between(startOfWeekDatetime, endOfWeekDateTime),
            Unavailability.unavailableEndTime.between(startOfWeekDatetime, endOfWeekDateTime)
        ).all()
        
        week_unavailability_list = [
            {
            "day": entry.unavailableStartTime.strftime('%A'),
            "date": entry.unavailableStartTime.strftime('%Y-%m-%d'),
            "startTime": entry.unavailableStartTime.strftime('%H:%M'),
            "endTime": entry.unavailableEndTime.strftime('%H:%M')
            } for entry in week_unavailability
        ]
        
    
        curr_employee = Employee.query.where(Employee.employeeID == current_user.employeeID).first()
        return jsonify({'availability': week_unavailability_list, 'name': curr_employee.firstName})
   
    except Exception as e:
        print(f"Error clearing availability: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/add_availability', methods=['POST'])
@login_required
def add_availability():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    
    
    date = data.get('date')
    start_time_str = data.get('startTime')
    end_time_str = data.get('endTime')

    if not all([date, start_time_str, end_time_str]):
        return jsonify({'success': False, 'error': 'Missing data fields'}), 400

    try:
        date = date.replace('T', ' ').replace('Z', '') 
        day_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f') 
        
        start_time = datetime.strptime(start_time_str, "%H:%M").time()  
        end_time = datetime.strptime(end_time_str, "%H:%M").time()  

        start_time_datetime = datetime.combine(day_date.date(), start_time)  
        end_time_datetime = datetime.combine(day_date.date(), end_time)
        
        new_unavailable_slot = Unavailability(
            employeeID=current_user.employeeID,
            unavailableStartTime=start_time_datetime,
            unavailableEndTime=end_time_datetime
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



    date_str = data.get('date') 
    start_time_str = data.get('startTime')  
    end_time_str = data.get('endTime') 

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        start_time = datetime.strptime(start_time_str, '%H:%M').time() 
        end_time = datetime.strptime(end_time_str, '%H:%M').time()

        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        slot_to_delete = Unavailability.query.filter_by(
            employeeID=current_user.employeeID,
            unavailableStartTime=start_datetime,
            unavailableEndTime=end_datetime
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


@main_blueprint.route('/clear_availability', methods=['POST'])
@login_required
def clear_availability(): 
    
    data = request.get_json()
    strStartOfWeek = data.get('startOfWeek')
    start = datetime.strptime(strStartOfWeek, '%Y-%m-%d').date()
    startOfWeek, endOfWeek = getWeekBounds(start)
    startOfWeekDatetime = datetime.combine(startOfWeek, datetime.min.time())
    endOfWeekDateTime = datetime.combine(endOfWeek, datetime.min.time())

 
    try:
        if not startOfWeek or not endOfWeek:
            return jsonify({'success': False, 'error': 'Missing year or week parameter'}), 400

        week_unavailability = Unavailability.query.filter(
            Unavailability.employeeID == current_user.employeeID,
            Unavailability.unavailableStartTime >= startOfWeekDatetime,
            Shift.shiftEndTime <= endOfWeekDateTime
        ).all()
        
        for entry in week_unavailability: 
            db.session.delete(entry)
            db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error clearing availability: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500


    

@main_blueprint.route('/unavailability', methods=['GET'])
@login_required
def unavailability_page():
    return render_template('unavailability.html')


@main_blueprint.route('/generate_schedule_page', methods=['GET'])
def create_schedule_page():
    return render_template('generateSchedule.html')


@main_blueprint.route('/generate_schedule', methods=['GET'])
@login_required
def generate_schedule():
    """
    Test endpoint to generate the schedule and return it as JSON.
    """
    try:
        employees = getEmployees()
        if not employees:
            print("No active employees found.")
            return jsonify({"success": False, "message": "No active employees found."}), 404

        availability = getAvailabilityDict(employees)
        
        newSchedule = generateSchedule(availability)

        formatted_schedule = {}
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for day_index, day_schedule in enumerate(newSchedule):
            formatted_schedule[day_names[day_index]] = []
            for slot_index, employees_in_slot in enumerate(day_schedule):
                if employees_in_slot:
                    hour = slot_index // 2
                    minute = "30" if slot_index % 2 else "00"
                    time_str = f"{hour:02d}:{minute}"
                    formatted_schedule[day_names[day_index]].append({
                        'time': time_str,
                        'employees': employees_in_slot
                    })

        print("Generated Schedule:")
        for day, slots in formatted_schedule.items():
            print(f"{day}:")
            for slot in slots:
                print(f"  {slot['time']} - Employees: {slot['employees']}")
            print("\n")

        return jsonify({"success": True, "schedule": formatted_schedule}), 200
    except Exception as e:
        print(f"Error generating schedule: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

    
    
    
@main_blueprint.route('/approve_schedule', methods=['POST'])
@login_required
def approve_schedule():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid data."}), 400
        
        next_monday = (datetime.today() + timedelta(days=7 - datetime.today().weekday())).date()
        day_dates = days_to_dates(next_monday)
        
        schedule = data['schedule'] if data['schedule'] else None
        print("This is the approved schedule " + str(schedule))
        for day, slots in schedule.items():
            day_date = day_dates[day]
            for slot in slots: 
                time = slot['time']
                employees = slot['employees']
                
                shift_start_time = datetime.strptime(time, "%H:%M").time()
                shift_end_time = (datetime.combine(datetime.today(), shift_start_time) + timedelta(minutes=30)).time()
                
                
                new_shift = Shift(
                    shiftStartTime=datetime.combine(datetime(2001, 1, 1), shift_start_time), 
                    shiftEndTime=datetime.combine(datetime(2001, 1, 1), shift_end_time)
                )
                db.session.add(new_shift)
                db.session.flush() 

                for employee_id in employees:
                    new_shift_assignment = ShiftAssignment(
                        shiftID=new_shift.shiftID,
                        employeeID=employee_id
                    )
                    db.session.add(new_shift_assignment)

        db.session.commit()
        return ({"success": True, "message": f"Successfully generated new schedule!"}), 500
        
    except Exception as e:
        db.session.rollback()
        print(f"Error approving schedule: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500


    
def next_week_start_date():
    return (datetime.today() + timedelta(days=7 - datetime.today().weekday())).date()

    
def days_to_dates(target_monday):
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_name_to_date = {}
    
    for i, day_name in enumerate(day_names):
        day_date = target_monday + timedelta(days=i)
        day_name_to_date[day_name] = day_date
    
    return day_name_to_date
    
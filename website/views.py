from flask import Blueprint, render_template, redirect, url_for
from flask import request, jsonify, json
from website.models import User, Employee, Unavailability, Shift, ShiftAssignment, Notification, Event
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
    admin_status = curr_employee.isAdmin
    if admin_status == True:
        admin_status = "Admin"
    else:
        admin_status = "Employee"    

    return render_template('schedule.html', fname=curr_employee.firstName, lname=curr_employee.lastName, wage=curr_employee.wage, gyear = curr_employee.gradYear, email=current_user.email, admin=admin_status, maxHours = curr_employee.maxHours, minHours=curr_employee.minHours)


def get_week_bounds(date):
    year, week = map(int, date.split('-W'))
    week_start_date = datetime.strptime(f'{year} {week} 1', '%G %V %u')
    week_end_date = week_start_date + timedelta(days=6)
    return week_start_date, week_end_date

def get_previous_week_bounds(date):
    year, week = map(int, date.split('-W'))
    if week > 1:
        week -= 1
    else:
        year -= 1
        week = datetime.strptime(f'{year}-12-31', '%Y-%m-%d').isocalendar()[1]
    
    week_start_date = datetime.strptime(f'{year} {week} 1', '%G %V %u')
    week_end_date = week_start_date + timedelta(days=6)
    return week_start_date, week_end_date

@main_blueprint.route('/get_schedule', methods=['POST'])
@login_required
def get_schedule():
    schedule_date = request.form.get('scheduleDate')
    try:
        week_start_date, week_end_date = get_week_bounds(schedule_date)
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
    except Exception as e:
        print(f"Error retrieving schedule: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/get_notifications', methods=['GET'])
@login_required
def get_notifications():
    try:
        notifications = (
            db.session.query(Notification)
            .filter(Notification.employeeID == current_user.employeeID)
            .order_by(Notification.sendTime.desc()) 
            .all()
        )

        return jsonify({
            "notifications": [
                {
                    "notificationID": notification.notificationID,
                    "message": notification.message,
                    "hasRead": notification.hasRead,
                    "sendTime": notification.sendTime.isoformat()
                }
                for notification in notifications
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@main_blueprint.route('/clear_notifications', methods=['POST'])
@login_required
def clear_notifications():
    try:
        Notification.query.filter_by(employeeID=current_user.employeeID).delete()
        db.session.commit()
        return jsonify({"success": True, "message": "All notifications cleared."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@main_blueprint.route('/mark_notifications_read', methods=['POST'])
@login_required
def mark_notifications_read():
    try:
        # Fetch all unread notifications for the current user
        unread_notifications = (
            Notification.query
            .filter_by(employeeID=current_user.employeeID, hasRead=False)
            .all()
        )

        # Mark all notifications as read
        for notification in unread_notifications:
            notification.hasRead = True
        
        # Commit the changes to the database
        db.session.commit()
        return jsonify({"success": True, "message": "All notifications marked as read."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@main_blueprint.route('/unavailability', methods=['GET'])
@login_required
def unavailability():
    curr_employee = Employee.query.where(Employee.employeeID == current_user.employeeID).first()

    admin_status = curr_employee.isAdmin
    if admin_status == True:
        admin_status = "Admin"
    else:
        admin_status = "Employee"    

    return render_template('unavailability.html', fname=curr_employee.firstName, lname=curr_employee.lastName, wage=curr_employee.wage, gyear = curr_employee.gradYear, email=current_user.email, admin=admin_status, maxHours = curr_employee.maxHours, minHours=curr_employee.minHours)

@main_blueprint.route('/get_unavailability', methods=['POST'])
@login_required
def get_availability(): 
    unavailability_date = request.form.get('unavailabilityDate')
    try:
        week_start_date, week_end_date = get_week_bounds(unavailability_date)
        print(f"Week Start: {week_start_date}, Week End: {week_end_date}")

        unavailability_for_week = (
            db.session.query(Unavailability)
            .filter(Unavailability.employeeID == current_user.employeeID)
            .filter(Unavailability.unavailableStartTime >= week_start_date, Unavailability.unavailableEndTime <= week_end_date)
            .all()
        )
        
        return jsonify({
            "unavailability": [
                {"unavailabilityID": unavailability.unavailabilityID, "start": unavailability.unavailableStartTime.isoformat(), "end": unavailability.unavailableEndTime.isoformat()}
                for unavailability in unavailability_for_week
            ]
        })
    except Exception as e:
        print(f"Error retrieving unavailability: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/add_unavailability', methods=['POST'])
@login_required
def add_unavailability():
    unavailable_start = request.form.get('unavailableStartTime')
    unavailable_end = request.form.get('unavailableEndTime')
    
    try:
        print(f"unavailable_start: {unavailable_start}, unavailable_end: {unavailable_end}")
        unavailable_start_date = datetime.fromisoformat(unavailable_start)
        unavailable_end_date = datetime.fromisoformat(unavailable_end)

        # Find overlapping unavailability periods
        overlapping_intervals = (Unavailability.query
                                 .filter(Unavailability.employeeID == current_user.employeeID)
                                 .filter(Unavailability.unavailableEndTime > unavailable_start_date)
                                 .filter(Unavailability.unavailableStartTime < unavailable_end_date)
                                 .order_by(Unavailability.unavailableStartTime)
                                 .all())

        # Start with the new unavailability as the base
        merge_start = unavailable_start_date
        merge_end = unavailable_end_date

        # Merge with the overlapping intervals
        for interval in overlapping_intervals:
            # If the existing interval overlaps with the new one, merge them
            if interval.unavailableStartTime <= merge_end and interval.unavailableEndTime >= merge_start:
                # Merge by extending the period to the earliest start time and latest end time
                merge_start = min(merge_start, interval.unavailableStartTime)
                merge_end = max(merge_end, interval.unavailableEndTime)
                # Remove the old overlapping interval
                db.session.delete(interval)

        # Create and add the merged unavailability period
        merged_unavailability = Unavailability(
            employeeID=current_user.employeeID,
            unavailableStartTime=merge_start,
            unavailableEndTime=merge_end
        )
        db.session.add(merged_unavailability)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Unavailability added successfully'})

    except Exception as e:
        db.session.rollback()
        print(f"Error adding unavailability: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/delete_unavailability', methods=['POST'])
@login_required
def delete_unavailability():
    unavailability_id = request.form.get('unavailabilityID')
    
    try:
        # Find the unavailability record by ID
        unavailability = Unavailability.query.filter_by(unavailabilityID=unavailability_id, employeeID=current_user.employeeID).first()
        if unavailability:
            # Delete the record
            db.session.delete(unavailability)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Unavailability deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Unavailability not found'}), 404
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting unavailability: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/clear_unavailability', methods=['POST'])
@login_required
def clear_unavailability():
    unavailability_date = request.form.get('unavailabilityDate')
    
    try:
        week_start_date, week_end_date = get_week_bounds(unavailability_date)
        print(f"Week Start: {week_start_date}, Week End: {week_end_date}")

        # Delete unavailability for the current week
        unavailability_to_delete = (
            db.session.query(Unavailability)
            .filter(Unavailability.employeeID == current_user.employeeID)
            .filter(Unavailability.unavailableStartTime >= week_start_date, Unavailability.unavailableEndTime <= week_end_date)
            .all()
        )

        # Check if there are any unavailability records to delete
        if len(unavailability_to_delete) > 0:
            for unavailability in unavailability_to_delete:
                db.session.delete(unavailability)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Unavailability for the current week has been cleared successfully'})
        else:
            return jsonify({'success': True, 'message': 'No unavailability records found for the current week to clear'})

    except Exception as e:
        db.session.rollback()
        print(f"Error clearing unavailability: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/autofill_unavailability', methods=['POST'])
@login_required
def autofill_unavailability():
    unavailability_date = request.form.get('unavailabilityDate')
    
    try:
        clear_unavailability()
        week_start_date, week_end_date = get_previous_week_bounds(unavailability_date)
        print(f"Week Start: {week_start_date}, Week End: {week_end_date}")

        # Get unavailability for the previous week
        unavailability_to_autofill = (
            db.session.query(Unavailability)
            .filter(Unavailability.employeeID == current_user.employeeID)
            .filter(Unavailability.unavailableStartTime >= week_start_date, Unavailability.unavailableEndTime <= week_end_date)
            .all()
        )

        # Check if there are any unavailability records to autofill
        if len(unavailability_to_autofill) > 0:
            for unavailability in unavailability_to_autofill:
                new_unavailability = Unavailability(
                    employeeID=current_user.employeeID,
                    unavailableStartTime=unavailability.unavailableStartTime + timedelta(weeks=1),
                    unavailableEndTime=unavailability.unavailableEndTime + timedelta(weeks=1)
                )
                # Add to the database session and commit
                db.session.add(new_unavailability)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Unavailability for the current week has been autofilled successfully'})
        else:
            return jsonify({'success': True, 'message': 'No unavailability records found for the previous week to autofill'})
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing unavailability: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/events', methods=['GET'])
@login_required
def events():
    curr_employee = Employee.query.where(Employee.employeeID == current_user.employeeID).first()

    admin_status = curr_employee.isAdmin
    if admin_status == True:
        admin_status = "Admin"
    else:
        admin_status = "Employee"    

    return render_template('events.html', fname=curr_employee.firstName, lname=curr_employee.lastName, wage=curr_employee.wage, gyear = curr_employee.gradYear, email=current_user.email, admin=admin_status, maxHours = curr_employee.maxHours, minHours=curr_employee.minHours)

@main_blueprint.route('/get_events', methods=['POST'])
@login_required
def get_events(): 
    events_date = request.form.get('eventsDate')
    try:
        week_start_date, week_end_date = get_week_bounds(events_date)
        print(f"Week Start: {week_start_date}, Week End: {week_end_date}")

        events_for_week = (
            db.session.query(Event)
            .filter(Event.eventStartTime >= week_start_date, Event.eventStartTime <= week_end_date)
            .all()
        )

        return jsonify({
            "events": [
                {"eventID": event.eventID, "start": event.eventStartTime.isoformat(), "end": event.eventEndTime.isoformat()}
                for event in events_for_week
            ]
        })
    except Exception as e:
        print(f"Error retrieving event: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/add_event', methods=['POST'])
@login_required
def add_event(): 
    event_host = request.form.get('eventHost')
    event_name = request.form.get('eventName')
    event_start = request.form.get('eventStartTime')
    event_end = request.form.get('eventEndTime')
    event_description = request.form.get('eventDescription')
    
    try:
        print(f"event_start: {event_start}, event_end: {event_end}")
        event_start_date = datetime.fromisoformat(event_start)
        event_end_date = datetime.fromisoformat(event_end)

        # Find overlapping unavailability periods
        overlapping_intervals = (Event.query
                                 .filter(Event.eventEndTime > event_start_date)
                                 .filter(Event.eventStartTime < event_end_date)
                                 .order_by(Event.eventStartTime)
                                 .all())

        # Start with the new unavailability as the base
        merge_start = event_start_date
        merge_end = event_end_date

        # Merge with the overlapping intervals
        for interval in overlapping_intervals:
            # If the existing interval overlaps with the new one, merge them
            if interval.eventStartTime <= merge_end and interval.eventEndTime >= merge_start:
                # Merge by extending the period to the earliest start time and latest end time
                merge_start = min(merge_start, interval.eventStartTime)
                merge_end = max(merge_end, interval.eventEndTime)
                # Remove the old overlapping interval
                db.session.delete(interval)

        # Create and add the merged unavailability period
        merged_event = Event(
            eventHost = event_host,
            eventName = event_name,
            eventStartTime=merge_start,
            eventEndTime=merge_end,
            eventDescription = event_description,
        )
        db.session.add(merged_event)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Event added successfully'})

    except Exception as e:
        db.session.rollback()
        print(f"Error adding event: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/delete_event', methods=['POST'])
@login_required
def delete_event():
    event_id = request.form.get('eventID')
    
    try:
        # Find the event record by ID
        event = Event.query.filter_by(eventID=event_id).first()
        if event:
            # Delete the record
            db.session.delete(event)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Event deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting event: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500
    
    

@main_blueprint.route('/clear_events', methods=['POST'])
@login_required
def clear_events():
    events_date = request.form.get('eventsDate')
    
    try:
        week_start_date, week_end_date = get_week_bounds(events_date)
        print(f"Week Start: {week_start_date}, Week End: {week_end_date}")

        # Delete unavailability for the current week
        events_to_delete = (
            db.session.query(Event)
            .filter(Event.eventStartTime >= week_start_date, Event.eventEndTime <= week_end_date)
            .all()
        )

        # Check if there are any unavailability records to delete
        if len(events_to_delete) > 0:
            for event in events_to_delete:
                db.session.delete(event)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Events for the current week has been cleared successfully'})
        else:
            return jsonify({'success': True, 'message': 'No event records found for the current week to clear'})

    except Exception as e:
        db.session.rollback()
        print(f"Error clearing event: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@main_blueprint.route('/generate_schedule_page', methods=['GET'])
def create_schedule_page():
    return render_template('generateSchedule.html')

@main_blueprint.route('/generate_schedule', methods=['POST'])
@login_required
def generate_schedule():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Missing start_date parameter."}), 400
        
        try:
            start_date = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
            if start_date.weekday() != 0: 
                return jsonify({"success": False, "message": "start_date must be a Monday."}), 400
        except ValueError:
            return jsonify({"success": False, "message": "Invalid start_date format. Use YYYY-MM-DD."}), 400
        
        employees = getEmployees()
        print("This is employees! ", employees)
        if not employees:
            print("No active employees found.")
            return jsonify({"success": False, "message": "No active employees found."}), 404

        availability = getAvailabilityDict(employees, start_date)
        newSchedule = generateSchedule(availability, start_date)

        formatted_schedule = {}
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        
        employees = Employee.query.filter(Employee.employeeID.in_(availability.keys())).all()
        employee_dict = {emp.employeeID: emp for emp in employees}

        for day_index, day_schedule in enumerate(newSchedule):
            day_date = start_date + timedelta(days=day_index)
            formatted_schedule[day_names[day_index]] = {
                "date": day_date.strftime("%Y-%m-%d"),
                "slots": []
            }
            for slot_index, employees_in_slot in enumerate(day_schedule):
                if employees_in_slot:
                    hour = slot_index // 2
                    minute = "30" if slot_index % 2 else "00"
                    time_str = f"{hour:02d}:{minute}"

                    # Convert each employee_id to {id: employee_id, name: employee_name}
                    detailed_employees = [
                        {"id": emp_id, "name": f"{employee_dict[emp_id].firstName} {employee_dict[emp_id].lastName[:1]}"}
                        for emp_id in employees_in_slot
                    ]

                    formatted_schedule[day_names[day_index]]["slots"].append({
                        'time': time_str,
                        'employees': detailed_employees
                    })   
                    
        return jsonify({"success": True, "schedule": formatted_schedule}), 200
    except Exception as e:
        print(f"Error generating schedule: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500
    
@main_blueprint.route('/approve_schedule', methods=['POST'])
@login_required
def approve_schedule():
    try:
        data = request.get_json()
        if not data or 'schedule' not in data or 'start_date' not in data:
            return jsonify({"success": False, "message": "Missing schedule or start_date in request data."}), 400

        start_date_str = data['start_date']
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if start_date.weekday() != 0: 
                return jsonify({"success": False, "message": "start_date must be a Monday."}), 400
        except ValueError:
            return jsonify({"success": False, "message": "Invalid start_date format. Use YYYY-MM-DD."}), 400
        
        
        end_date = start_date + timedelta(days=6)
        
        existing_shifts = (
            db.session.query(Shift)
            .filter(Shift.shiftStartTime >= start_date)
            .filter(Shift.shiftEndTime <= end_date + timedelta(days=1))  
            .first()
        )

        if existing_shifts:
            return jsonify({"success": False, "message": "A schedule for this week already exists."}), 400


        schedule = json.loads(data['schedule']) if isinstance(data['schedule'], str) else data['schedule']
        print("this is schedule", schedule)
        scheduled_workers = set()

        day_dates = {day: start_date + timedelta(days=index) for index, day in enumerate(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}

        for day, day_data in schedule.items():
            day_date = day_dates.get(day)
            if not day_date:
                continue  
            slots = day_data.get('slots', [])
            for slot in slots:
                time = slot['time']
                employees = slot['employees']

                shift_start_time = datetime.strptime(time, "%H:%M").time()
                shift_end_time = (datetime.combine(day_date, shift_start_time) + timedelta(minutes=30)).time()

                new_shift = Shift(
                    shiftStartTime=datetime.combine(day_date, shift_start_time),
                    shiftEndTime=datetime.combine(day_date, shift_end_time)
                )
                db.session.add(new_shift)
                db.session.flush() 

                for employee in employees:
                    employee_id = employee['id'] 
                    scheduled_workers.add(employee_id)
                    new_shift_assignment = ShiftAssignment(
                        shiftID=new_shift.shiftID,
                        employeeID=employee_id
                    )
                    db.session.add(new_shift_assignment)

        for employee in scheduled_workers:
            new_notification = Notification(
                message=f"A new schedule has been published for the week of {start_date.strftime('%B %d, %Y')}",
                hasRead=False,
                employeeID=employee
            )
            db.session.add(new_notification)

        db.session.commit()
        return jsonify({"success": True, "message": "Successfully approved the schedule!"}), 200

    except Exception as e:
        db.session.rollback() 
        print(f"Error approving schedule: {e}")
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

    
@main_blueprint.route('/admin', methods=['GET'])
@login_required
def admin_page():
    
    #will update this logic with emails as we approach demo
    # allowed_admin_emails = []
    # if current_user.email not in allowed_admin_emails:
    #     return "Access denied", 403
    
    
    date = next_week_start_date()
    print("This is date", date)
    return render_template('admin.html', current_week = date)






def next_week_start_date():
    return (datetime.today() + timedelta(days=7 - datetime.today().weekday())).date()

    
def days_to_dates(target_monday):
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_name_to_date = {}
    
    for i, day_name in enumerate(day_names):
        day_date = target_monday + timedelta(days=i)
        day_name_to_date[day_name] = day_date
    
    return day_name_to_date
    
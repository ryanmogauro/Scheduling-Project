from website.models import User, Employee, Unavailability, Shift, ShiftAssignment
from datetime import datetime, timedelta
from website import db


def getDailyOperatingHours():
    return {
        0: (7.5, 17.5),  
        1: (7.5, 17.5),
        2: (7.5, 17.5),
        3: (7.5, 17.5),
        4: (7.5, 17.5),
        5: (0, 0),       
        6: (9.5, 16.5),  
    }


def getEmployees():
    currentEmployees = User.query.filter(User.isActive == True).all()
    currentEmployeeIDs = [emp.employeeID for emp in currentEmployees]
    print("Current Employee IDs:", currentEmployeeIDs)
    return currentEmployeeIDs


def getUnavailability(employeeID, start_date):
    end_date = start_date + timedelta(days=6)
    unavailability = (
        Unavailability.query
        .filter(
            Unavailability.employeeID == employeeID,
            Unavailability.unavailableStartTime >= datetime.combine(start_date, datetime.min.time()),
            Unavailability.unavailableEndTime <= datetime.combine(end_date, datetime.max.time())
        )
        .all()
    )
    return unavailability


def getAvailabilityDict(employees, start_date):
    availability = {emp_id: [[1] * 48 for _ in range(7)] for emp_id in employees}

    for employee_id in employees:
        unavailability = getUnavailability(employee_id, start_date)

        for entry in unavailability:
            day_index = (entry.unavailableStartTime.date() - start_date).days

            if day_index < 0 or day_index > 6:
                continue

            start_hour = entry.unavailableStartTime.hour + entry.unavailableStartTime.minute / 60
            end_hour = entry.unavailableEndTime.hour + entry.unavailableEndTime.minute / 60
            start_block = int(start_hour * 2)
            end_block = int(end_hour * 2)

            if end_block < start_block:
                end_block += 48 

            for block in range(start_block, end_block):
                current_block = block % 48
                availability[employee_id][day_index][current_block] = 0

    return availability


def isAvailable(employee, availability, day, shiftSlot):
    return availability[employee][day][shiftSlot] == 1

def validRolloverShift(schedule, day, shiftSlot, employee):
    consecutiveTime = 0
    shift = shiftSlot - 1
    opening = int(getDailyOperatingHours()[day][0] * 2)

    while shift >= opening and employee in schedule[day][shift]:
        consecutiveTime += 0.5
        shift -= 1
    return consecutiveTime < 2.5


def generateSchedule(availability, start_date):
    if start_date.weekday() != 0:
        raise ValueError("start_date must be a Monday.")

    employees = Employee.query.filter(Employee.employeeID.in_(availability.keys())).all()

    employee_info = {}
    for emp in employees:
        employee_info[emp.employeeID] = {
            "minHours": emp.minHours if emp.minHours else 0,
            "maxHours": emp.maxHours if emp.maxHours else 40,
            "assignedHours": 0.0
        }

    schedule = [[[] for _ in range(48)] for _ in range(7)]
    dailyOperatingHours = getDailyOperatingHours()
    issues = []

    for day_offset, hours in dailyOperatingHours.items():
        current_date = start_date + timedelta(days=day_offset)
        open_block = int(hours[0] * 2)
        close_block = int(hours[1] * 2)

        for shiftSlot in range(open_block, close_block):
           
            if shiftSlot > open_block:
                for employee in schedule[day_offset][shiftSlot - 1]:
                    if (
                        isAvailable(employee, availability, day_offset, shiftSlot)
                        and validRolloverShift(schedule, day_offset, shiftSlot, employee)
                    ):
                        if len(schedule[day_offset][shiftSlot]) < 2:
                            schedule[day_offset][shiftSlot].append(employee)
                         
                            employee_info[employee]["assignedHours"] += 0.5

            if len(schedule[day_offset][shiftSlot]) < 2:
                availableEmployees = [
                    emp_id for emp_id in availability
                    if isAvailable(emp_id, availability, day_offset, shiftSlot) 
                    and emp_id not in schedule[day_offset][shiftSlot]
                ]

                if not availableEmployees and len(schedule[day_offset][shiftSlot]) == 0:
                    issues.append(f"No employees available on {current_date}, Slot {shiftSlot}.")
                    continue

                # Sort the available employees based on how well they fit:
                # Score calculation:
                # - Give a bonus if they haven't reached their minHours (encourage giving them more hours)
                # - Within that, prefer employees who are farthest from their maxHours
                def employee_score(e):
                    info = employee_info[e]
                    current_hours = info["assignedHours"]
                    min_hours = info["minHours"]
                    max_hours = info["maxHours"]
                    
                    max_gap = max_hours - current_hours
                    
                    bonus = 100 if current_hours < min_hours else 0
                
                    return bonus + max_gap

                availableEmployees.sort(key=employee_score, reverse=True)

                for candidate in availableEmployees:
                    if len(schedule[day_offset][shiftSlot]) >= 2:
                        break
                    if validRolloverShift(schedule, day_offset, shiftSlot, candidate):
                        schedule[day_offset][shiftSlot].append(candidate)
                        employee_info[candidate]["assignedHours"] += 0.5


    for issue in issues:
        print(f"Issue: {issue}")

    return schedule
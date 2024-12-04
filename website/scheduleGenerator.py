from website.models import User, Employee, Unavailability, Shift, ShiftAssignment
from datetime import datetime, timedelta
from website import db


# 0 -> Monday
# 6 -> Sunday

def getDailyOperatingHours():
    """
    Returns the daily operating hours for the week.
    Each day corresponds to a tuple of (open hour, close hour).
    """
    return {
        0: (7.5, 17.5),  # Monday
        1: (7.5, 17.5),  # Tuesday
        2: (7.5, 17.5),  # Wednesday
        3: (7.5, 17.5),  # Thursday
        4: (7.5, 17.5),  # Friday
        5: (0, 0),       # Saturday
        6: (9.5, 16.5),  # Sunday
    }

def getEmployees():
    currentEmployees = User.query.filter(User.isActive == True).all()
    currentEmployeeIDs = [emp.employeeID for emp in currentEmployees]
    print("Current Employee IDs:", currentEmployeeIDs)
    return currentEmployeeIDs
    
    
def getUnavailability(employeeID, start_date):
    end_date = start_date + timedelta(days=6)

    # Query unavailability within the date range
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

            # Ignore entries outside the week (shouldn't happen due to filtering in `getUnavailability`)
            if day_index < 0 or day_index > 6:
                continue

            # Convert unavailable times into blocks
            start_hour = entry.unavailableStartTime.hour + entry.unavailableStartTime.minute / 60
            end_hour = entry.unavailableEndTime.hour + entry.unavailableEndTime.minute / 60
            start_block = int(start_hour * 2)
            end_block = int(end_hour * 2)

            if end_block < start_block:
                end_block += 48  # Handle overnight unavailability

            for block in range(start_block, end_block):
                current_block = block % 48  # Ensure block is within valid range
                availability[employee_id][day_index][current_block] = 0

    return availability

def isAvailable(employee, availability, day, shiftSlot):
    return availability[employee][day][shiftSlot] == 1



def validRolloverShift(schedule, day, shiftSlot, employee):
    """
    Ensures an employee doesn't work for more than 2.5 consecutive hours.
    """
    consecutiveTime = 0
    shift = shiftSlot - 1
    opening = int(getDailyOperatingHours()[day][0] * 2)

    while shift >= opening and employee in schedule[day][shift]:
        consecutiveTime += 0.5
        shift -= 1

    return consecutiveTime < 2.5

def generateSchedule(availability, start_date):
    """
    Generates a weekly schedule based on employee availability and a given start date (Monday).
    
    Parameters:
        availability (dict): Dictionary of employee availability.
        start_date (date): Start date of the week (must be a Monday).
    
    Returns:
        list: Weekly schedule (list of days with 48 time slots each).
    """
    if start_date.weekday() != 0:
        raise ValueError("start_date must be a Monday.")

    schedule = [[[] for _ in range(48)] for _ in range(7)]
    dailyOperatingHours = getDailyOperatingHours()
    issues = []

    for day_offset, hours in dailyOperatingHours.items():
        # Calculate the date for the current day
        current_date = start_date + timedelta(days=day_offset)
        open_block = int(hours[0] * 2)
        close_block = int(hours[1] * 2)

        for shiftSlot in range(open_block, close_block):
            # Check rollover employees
            if shiftSlot > open_block:
                for employee in schedule[day_offset][shiftSlot - 1]:
                    if (
                        isAvailable(employee, availability, day_offset, shiftSlot)
                        and validRolloverShift(schedule, day_offset, shiftSlot, employee)
                    ):
                        schedule[day_offset][shiftSlot].append(employee)

            # Assign new employees if needed
            availableEmployees = [
                emp_id for emp_id in availability if isAvailable(emp_id, availability, day_offset, shiftSlot)
            ]

            if not availableEmployees:
                issues.append(f"No employees available on {current_date}, Slot {shiftSlot}.")
                continue

            for employee in availableEmployees:
                if len(schedule[day_offset][shiftSlot]) >= 2:  # Max two employees per slot
                    break
                if employee not in schedule[day_offset][shiftSlot]:
                    schedule[day_offset][shiftSlot].append(employee)

    # Print any scheduling issues
    for issue in issues:
        print(f"Issue: {issue}")

    return schedule



def main():
    employees = getEmployees()
    availability = getAvailabilityDict(employees)
    newSchedule = generateSchedule(availability)
    
    for day_index, day_schedule in enumerate(newSchedule):
        print(f"Day {day_index}:")
        for slot, employees in enumerate(day_schedule):
            if employees:
                hour = slot // 2
                minute = "30" if slot % 2 else "00"
                print(f"  {hour}:{minute} - Employees: {employees}")
        print("\n")

if __name__ == "__main__":
    main()

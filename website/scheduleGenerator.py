from website.models import User, Employee, Unavailability, Shift, ShiftAssignment
from datetime import datetime
from website import db


# 0 -> Monday
# 6 -> Sunday
dailyOperatingHours = {
    0: (7.5, 17.5),
    1: (7.5, 17.5), 
    2: (7.5, 17.5), 
    3: (7.5, 17.5),
    4: (7.5, 17.5),
    5: (0, 0),
    6: (9.5, 16.5)
}

def getEmployees():
    currentEmployees = User.query.filter(User.isActive == True).all()
    currentEmployeeIDs = [emp.employeeID for emp in currentEmployees]
    print("Current Employee IDs:", currentEmployeeIDs)
    return currentEmployeeIDs
    
    
def getUnavailability(employeeID):
    unavailability = Unavailability.query.filter(Unavailability.employeeID == employeeID).all()
    return unavailability


def getAvailabilityDict(employees):
    availability = {}
    for employee_id in employees:
        # 48 time slots in a day, 7 days
        # 1 -> available, 0 -> unavailable
        employeeAvailability = [[1 for _ in range(48)] for _ in range(7)]
        
        unavailability = getUnavailability(employee_id)
        
        for entry in unavailability:
            day_index = entry.unavailableStartTime.weekday()
            
            start_hour = entry.unavailableStartTime.hour + entry.unavailableStartTime.minute / 60
            end_hour = entry.unavailableEndTime.hour + entry.unavailableEndTime.minute / 60

            start_block = int(start_hour * 2)
            end_block = int(end_hour * 2)
            
            if end_block < start_block:
                end_block += 48  
            
            for block in range(start_block, end_block):
                current_block = block % 48  # Ensure block is within 0-47
                employeeAvailability[day_index][current_block] = 0
        
        availability[employee_id] = employeeAvailability
        
    return availability


def isAvailable(employee, availability, day, shiftSlot):
    return availability[employee][day][shiftSlot] == 1


def validRolloverShift(schedule, day, shiftSlot, employee):
    consecutiveTime = 0
    shift = shiftSlot - 1 
    opening = int(dailyOperatingHours[day][0] * 2)
    while shift >= opening and employee in schedule[day][shift]:
        consecutiveTime += 0.5
        shift -= 1
    
    return consecutiveTime < 2.5


def generateSchedule(availability):
    schedule = [[[] for _ in range(48)] for _ in range(7)]
    issues = []

    for day in dailyOperatingHours:
        open_block = int(dailyOperatingHours[day][0] * 2)
        close_block = int(dailyOperatingHours[day][1] * 2)
        
        for shiftSlot in range(open_block, close_block):
            #try rollover
            pastShiftEmployees = schedule[day][shiftSlot-1] if shiftSlot > open_block else []
            if pastShiftEmployees:
                for employee in pastShiftEmployees:
                    if isAvailable(employee, availability, day, shiftSlot) and validRolloverShift(schedule, day, shiftSlot, employee):
                        schedule[day][shiftSlot].append(employee)
            
            # if both employees can rollover
            if len(schedule[day][shiftSlot]) > 1:
                pass  # Implement any specific logic if needed
            
            availableEmployees = [emp_id for emp_id in availability if availability[emp_id][day][shiftSlot] == 1]
            
            if len(availableEmployees) == 0: 
                issues.append(f"No employees available at Day {day} Slot {shiftSlot}")
                pass  

            if len(availableEmployees) == 1: 
                issues.append(f"Only one available employee at Day {day} Slot {shiftSlot}")
                pass 
             
            k = 0
            while k < len(availableEmployees) and len(schedule[day][shiftSlot]) < 2:
                employee_to_assign = availableEmployees[k]
                if employee_to_assign not in schedule[day][shiftSlot]:
                    schedule[day][shiftSlot].append(employee_to_assign)
                k += 1
                
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

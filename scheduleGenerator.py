from models import db, User, Employee, Unavailability, Shift, ShiftAssignment

#0 -> Monday
#6 -> Sunday
dailyOperatingHours = {
    0 : (7.5, 17.5),
    1: (7.5, 17.5), 
    2: (7.5, 17.5), 
    3: (7.5, 17.5),
    4: (7.5, 17.5),
    5: (0, 0),
    6: (9.5, 4.5)
}

def getEmployees():
    # SQL statement to select all employee ids, where isActive
    return ['Ryan', 'Eli', 'Henry', 'Trey']
    
    
def getUnavailability(employee):
    #something like Unavailability.where(employeeID = id).all()
    dummy = {
        

        'Ryan' :  [
            [[7.5, 11], [13, 17]], 
            [[11,13]], 
            [[7,9], [16, 17]], 
            [[7,8], [1,3]],
            [[7,10], [13, 15]], 
            [[]], 
            [[7, 11]]
            ], 
        'Eli' : [
            [[13, 17]], 
            [[9, 10], [11,13]], 
            [[7,9]], 
            [],
            [[10, 12]], 
            [[]], 
            [[7, 15]]
            ], 
        'Henry' : [
            [[10, 11.5]], 
            [[11,16.5]], 
            [[9, 12], [13, 17]], 
            [[11, 15]],
            [[12, 14.5]], 
            [[]], 
            [[14, 15]]
            ], 
        'Trey' : [
            [[12.5, 15.5]], 
            [[7, 9.5]], 
            [[]], 
            [[11, 15]],
            [[]], 
            [[]], 
            [[]]
            ]
    }
    
    return dummy[employee]

    
def getAvailabilityDict(employees):
    availability = {}
    for id in employees:
        
        #48 time slots in a day, for 7 days
        #1 -> available, 0 -> unavailable
        employeeAvailability = [[1 for i in range(48)] for j in range(7)]
        
        
        unavailability = getUnavailability(id)
        
        
        for dayIndex, dayUnvailability in enumerate(unavailability): 
            for block in dayUnvailability: 
                #if employee free all day
                if not block: 
                    pass
            
                start = int(block[0]) if block else 0
                end = int(block[1]) if block else 0
                
                for shift in range(start, end): 
                    employeeAvailability[dayIndex][shift] = 0
            
            
        
        
        availability[id] = employeeAvailability
        
    return availability

def isAvailable(employee, availability, shiftSlot):
    return availability[shiftSlot] == 1


def validRolloverShift(schedule, day, shiftSlot, employee):
    consecutiveTime = 0
    shift = shiftSlot - 1 
    opening = int(dailyOperatingHours[day][0] * 2)
    while shift >= opening and employee in schedule[day][shift]:
        consecutiveTime += .5
        shift-=1
    
    return consecutiveTime <  2.5
        
    
        
    
    


def generateSchedule(availability):
    
    schedule = [[[] for i in range(48)] for j in range(7)]
    
    issues = []

    for day in dailyOperatingHours:
        open = int(dailyOperatingHours[day][0]*2)
        close = int(dailyOperatingHours[day][1]*2)
        
        for shiftSlot in range(open, close):
            
            #try past employees
            pastShiftEmployees = schedule[day][shiftSlot-1] if shiftSlot > open else None
            if pastShiftEmployees:
                for employee in pastShiftEmployees:
                    employeeAvailability = availability[employee][day] #because 0 indexing
                    if isAvailable(employee, employeeAvailability, shiftSlot) and validRolloverShift(schedule, day, shiftSlot, employee):
                        schedule[day][shiftSlot].append(employee)
            
            #if both employees can rollover
            if len(schedule[day][shiftSlot]) > 1:
                pass
            
            
            availableEmployees = [id for id in availability if availability[id][day][shiftSlot] == 1] #and under max hours?
            
            #would sort here, maybe by distance from hours limit
            
            if len(availableEmployees) == 0: 
                issues.append("No employees available at " + str(day) + " : " + str(shiftSlot))
                pass
        
            if len(availableEmployees) == 1: 
                issues.append("Only one available employee at " + str(day) + " : " + str(shiftSlot))
                pass
             
            k = 0
            while k < len(availableEmployees) and len(schedule[day][shiftSlot]) < 2:
                schedule[day][shiftSlot].append(availableEmployees[k])
                k+=1
            
                
    return schedule


        
            
employees = getEmployees()
availability = getAvailabilityDict(employees)
newSchedule = generateSchedule(availability)
for day in newSchedule: 
    print(day)
    print("\n")

    
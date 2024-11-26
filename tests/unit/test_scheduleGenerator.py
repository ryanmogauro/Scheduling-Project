import os
from website import create_app
from website.models import db, User, Employee
from website.scheduleGenerator import getEmployees, getUnavailability, isAvailable, validRolloverShift, generateSchedule
from flask_login import current_user, login_user

def test_getEmployees():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        employees = getEmployees()
        assert len(employees) > 0
    
    
def test_getUnavailability():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.post('/add_availability', json={'day' : 'Monday', 'startTime': "09:00", "endTime" : "11:00"})
        assert response.status_code == 200
        with flask_app.app_context():
            user = User.query.filter_by(email="flast@colby.edu").first()
            assert user is not None

            # Test getUnavailability function
            unavailability = getUnavailability(user.employeeID)
            assert len(unavailability) > 0
            assert unavailability[0].unavailableStartTime.strftime('%H:%M') == "09:00"
            assert unavailability[0].unavailableEndTime.strftime('%H:%M') == "11:00"
            
            

def test_isAvailable():
    availability = {1: [[1 for x in range(48)] for x in range(7)], }
    availability[1][0][18] = 0 

    assert isAvailable(1, availability, 0, 17) is True 
    assert isAvailable(1, availability, 0, 18) is False 


def test_validRolloverShift():
    schedule = [[[] for _ in range(48)] for _ in range(7)]
    schedule[0][18] = [1]  
    schedule[0][19] = [1] 

    assert validRolloverShift(schedule, 0, 20, 1) is True  # 10:00 AM

    schedule[0][20] = [1]  
    schedule[0][21] = [1]  
    schedule[0][22] = [1]  
    schedule[0][23] = [1] 
    schedule[0][24] = [1]
    assert validRolloverShift(schedule, 0, 25, 1) is False
    
    
    
    
def test_generateSchedule():

    availability = {
        1: [[1 for _ in range(48)] for _ in range(7)], 
        2: [[1 for _ in range(48)] for _ in range(7)]
    }
    availability[1][0][18] = 0
    availability[2][0][19] = 0
    
    schedule = generateSchedule(availability)

    assert len(schedule) == 7 
    assert len(schedule[0]) == 48  

    assert 1 not in schedule[0][18] 
    assert 2 not in schedule[0][19]
    assert len(schedule[0][20]) > 0
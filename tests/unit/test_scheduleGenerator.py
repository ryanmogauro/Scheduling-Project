import os
from website import create_app
from website.models import db, User, Employee
from website.scheduleGenerator import getEmployees, getUnavailability, isAvailable, validRolloverShift, generateSchedule
from flask_login import current_user, login_user
import datetime
import conftest

def test_getEmployees(test_client):
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        employees = getEmployees()
        assert len(employees) > 0
    
    
def test_getUnavailability(test_client):
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.post('/add_unavailability', data={'unavailableStartTime' : "2024-12-08T07:00:00.000", "unavailableEndTime" : "2024-12-08T08:00:00.000"})
        #response = test_client.post('/add_unavailability', json = {'success': True, 'message': 'Unavailability added successfully'})
        assert response.status_code == 200
        user = User.query.filter_by(email="flast@colby.edu").first()
        assert user is not None

        # Test getUnavailability function
        unavailability = getUnavailability(user.employeeID,datetime.datetime(2024,12,8,7,00,00,000))
        assert len(unavailability) > 0
        assert unavailability[0].unavailableStartTime.strftime('%H:%M') == "07:00"
        assert unavailability[0].unavailableEndTime.strftime('%H:%M') == "08:00"
            
            

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
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    flask_app_context = flask_app.app_context()
    
    flask_app_context.push()

    db.create_all()
    
    employee1 = Employee(firstName = "test",lastName = "1", employeeID=2, minHours=4, maxHours=12)
    employee2 = Employee(firstName = "test",lastName = "2", employeeID=3, minHours=4, maxHours=12)
    db.session.add(employee1)
    db.session.add(employee2)
    db.session.commit()
    with flask_app.test_client() as test_client:
        

        availability = {
            2: [[1 for _ in range(48)] for _ in range(7)], 
            3: [[1 for _ in range(48)] for _ in range(7)]
        }
        availability[2][0][18] = 0
        availability[3][0][19] = 0
        startDate = datetime.date(2024,12,2)
        
        schedule = generateSchedule(availability,startDate)

        assert len(schedule) == 7 
        assert len(schedule[0]) == 48  

        assert 2 not in schedule[0][18] 
        assert 3 not in schedule[0][19]
        assert len(schedule[0][20]) > 0
   
    db.session.rollback()
    db.drop_all()
    flask_app_context.pop()
    
import os
from website import create_app
from website.models import db, User, Employee
from flask_login import current_user
import json
import conftest



#Availability tests


def test_add_unavailability(test_client): 
    #os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    #flask_app = create_app()

    #with flask_app.test_client() as test_client:
        test_client.post('/', data = {
            'firstName' : 'first', 
            'lastName' : 'last',
            'email' : 'flast@colby.edu', 
            'password' : "longerPass" #too short
    },follow_redirects=True)
        
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.post('/add_unavailability', data={'unavailableStartTime' : "2024-12-08T07:00:00.000", "unavailableEndTime" : "2024-12-08T08:00:00.000"})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["success"] == True
        
        
def test_invalid_add_unavailability(test_client): 
    
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.post('/add_unavailability', json={})
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data["success"] == False


def test_unavailability_get(test_client):
   
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.get('/unavailability')
        assert response.status_code == 200 
        
def test_get_unavailability(test_client):  
    
    response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
    assert response.status_code == 200
    response = test_client.post('/add_unavailability', data={'unavailableStartTime' : "2024-12-07T07:00:00.000", "unavailableEndTime" : "2024-12-07T08:00:00.000"},follow_redirects=True)

        
    response = test_client.post('/get_unavailability',data = {'unavailabilityDate' : "2024-W49"})
    response_data = json.loads(response.data)
    assert response.status_code == 200
    assert "unavailability" in response_data 
    assert response_data["unavailability"]
    






#Schedule tests

def test_schedule_get(test_client):
    
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.get('/schedule', follow_redirects = True)
        assert response.status_code == 200
        assert b"Monday" in response.data
        assert b"Wednesday" in response.data

def test_schedule_admin(test_client):
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.get('/schedule', follow_redirects = True)
        assert response.status_code == 200
        assert b"Monday" in response.data
        assert b"Wednesday" in response.data





#generate schedule tests

def test_generate_schedule_page(test_client):
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.get('/generate_schedule_page', follow_redirects = True)
        assert response.status_code == 200
        assert b"Schedule Management" in response.data

def test_generate_schedule(test_client): 
            response = test_client.post('/login', data={
                'email': 'flast@colby.edu',
                'password': 'longerPass'
            }, follow_redirects=True)
            assert response.status_code == 200
            response = test_client.post('/generate_schedule', json = {'start_date': '2024-12-16'}, follow_redirects = True)
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data["success"] == True
            assert response_data["schedule"] 
            
            
def test_approve_schedule(test_client): 
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        response = test_client.post('/generate_schedule', json = {'start_date': '2024-12-16'}, follow_redirects = True)
        assert response.status_code == 200
        
        response_data = response.get_json()
        schedule = response_data.get("schedule")
        assert schedule is not None
        
        assert response.status_code == 200
        response = test_client.post('/approve_schedule', json={"schedule" : schedule, "start_date": "2024-12-16"}, follow_redirects = True)
        response_data = response.get_json()
        print(response_data)
        assert response_data["success"] is True
        assert response_data["message"] == "Successfully approved the schedule!"
        


def test_invalid_approve_schedule(test_client): 

        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        response = test_client.post('/generate_schedule', json = {'start_date': '2024-12-16'}, follow_redirects = True)
        assert response.status_code == 200
        
        response_data = response.get_json()
        schedule = response_data.get("schedule")
        assert schedule is not None
        
        assert response.status_code == 200
        response = test_client.post('/approve_schedule', json={}, follow_redirects = True)
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data["success"] is False
        assert response_data["message"] == "Missing schedule or start_date in request data."
        



import os
from website import create_app
from website.models import db, User, Employee
from flask_login import current_user
import json


#Availability tests


def test_add_unavailability(): 
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
        response_data = json.loads(response.data)
        assert response_data["success"] == True
        
        
def test_invalid_add_unavailability(): 
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.post('/add_availability', json={})
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["success"] == False


def test_unavailability_get():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.get('/unavailability')
        assert response.status_code == 200
        
        
def test_get_unavailability():   
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        
    response = test_client.get('/get_unavailability')
    response_data = json.loads(response.data)
    assert response.status_code == 200
    assert response_data["availability"]
    
def test_delete_availability():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.post('/delete_availability', json={'day' : 'Monday', 'startTime': "09:00", "endTime" : "11:00"})
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["success"] == True

def test_invalid_delete_availability():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.post('/delete_availability', json={})
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["success"] == False



#Schedule tests

def test_schedule_get():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as test_client:
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

def test_generate_schedule_page():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.get('/generate_schedule_page', follow_redirects = True)
        assert response.status_code == 200
        assert b"Schedule Management" in response.data

def test_generate_schedule(): 
        os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
        flask_app = create_app()

        with flask_app.test_client() as test_client:
            response = test_client.post('/login', data={
                'email': 'flast@colby.edu',
                'password': 'longerPass'
            }, follow_redirects=True)
            assert response.status_code == 200
            response = test_client.get('/generate_schedule', follow_redirects = True)
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data["success"] == True
            assert response_data["schedule"]
            
            
def test_approve_schedule(): 
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        response = test_client.get('/generate_schedule', follow_redirects = True)
        assert response.status_code == 200
        
        response_data = response.get_json()
        schedule = response_data.get("schedule")
        assert schedule is not None
        
        assert response.status_code == 200
        response = test_client.post('/approve_schedule', json={"schedule" : schedule}, follow_redirects = True)
        response_data = response.get_json()
        assert response_data["success"] is True
        assert response_data["message"] == "Successfully generated new schedule!"
        


def test_invalid_approve_schedule(): 
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        response = test_client.get('/generate_schedule', follow_redirects = True)
        assert response.status_code == 200
        
        response_data = response.get_json()
        schedule = response_data.get("schedule")
        assert schedule is not None
        
        assert response.status_code == 200
        response = test_client.post('/approve_schedule', json={}, follow_redirects = True)
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data["success"] is False
        assert response_data["message"] == "Invalid data."
        



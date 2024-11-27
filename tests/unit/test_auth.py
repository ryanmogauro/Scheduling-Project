import os
from website import create_app
from website.models import db, User, Employee
from werkzeug.security import generate_password_hash

#sign-up tests

def test_signup_page(): 
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    with flask_app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200
        assert b'Sign-up' in response.data
        assert b'name' in response.data
        assert b'password' in response.data
        
def test_user_set_password():
    user = User()
    user.set_password('password')
    assert user.passwordHash is not None
    assert user.passwordHash != 'password'
    
def test_user_check_password():
    user = User()
    user.set_password('password')
    assert user.check_password('password')
    assert not user.check_password('wrongpassword')
    
def test_invalid_signup():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    with flask_app.test_client() as test_client:
        response = test_client.post('/', data = {
            'firstName' : 'first', 
            'lastName' : 'last',
            'email' : 'flast@colby.edu', 
            'password' : "four" #too short
    },follow_redirects=True)
        
    assert response.status_code == 200
    
    #no flash messages yet, so this line won't trigger, but will need it
    #assert b'Password must be between 5 and 20 characters' in response.data
        
    
def test_valid_signup():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    with flask_app.test_client() as test_client:
        response = test_client.post('/', data = {
            'firstName' : 'first', 
            'lastName' : 'last',
            'email' : 'flast@colby.edu', 
            'password' : "longerPass" #too short
    },follow_redirects=True)
        
    assert response.status_code == 200
    assert b'Login' in response.data
    
    
    
    

#Login tests
       
def test_login_page(): 
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        response = test_client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data
        assert b'email' in response.data
        assert b'password' in response.data
        

def test_valid_login():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Schedule' in response.data #successful login directs to schedule
        
        
        
def test_invalid_user_login():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'user@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Schedule' not in response.data #unsuccessful login, will change with flashes
    
def test_invalid_password_login():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPas'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Schedule' not in response.data #unsuccessful login



 
#Log out test
def test_logout():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        response = test_client.post('/login', data={
            'email': 'flast@colby.edu',
            'password': 'longerPass'
        }, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data 
        
        
        

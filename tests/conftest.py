#credit to Naser Al Madi
import sys, os
#couldn't find website module before adding this line
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from website import create_app


@pytest.fixture()
def test_client():
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        yield test_client # this is where the testing happens!
        
        
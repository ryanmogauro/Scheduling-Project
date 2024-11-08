from flask import Flask
from models import db, User
from flask_login import LoginManager
from views import main_blueprint
from auth import auth_blueprint
import os

app = Flask(__name__)

uri = os.getenv('JAWSDB_URL', 'sqlite:///mydatabase.db')

# Adjust the URI if necessary
if uri.startswith('mysql://'):
    uri = uri.replace('mysql://', 'mysql+pymysql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.signup'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Register blueprint for routes
app.register_blueprint(main_blueprint)
app.register_blueprint(auth_blueprint)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables (if not created)
    app.run(debug=True)

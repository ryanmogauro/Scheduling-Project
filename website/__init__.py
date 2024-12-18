from flask import Flask
from flask_login import LoginManager
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_migrate import Migrate

# from sqlalchemy.exc import OperationalError
# from sqlalchemy.sql import text

from dotenv import load_dotenv
load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'secret keyyyyy'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('JAWSDB_URL') or 'sqlite:///mydatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
    db.init_app(app)
    migrate = Migrate(app, db)
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.signup'

    from .models import User
    from .views import main_blueprint
    from .auth import auth_blueprint

    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Register blueprint for routes
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    # if __name__ == '__main__':
    with app.app_context():

        db.create_all()  # Create tables (if not created)

    
    return app

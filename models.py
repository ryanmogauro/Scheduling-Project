from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


db = SQLAlchemy()

class User(db.Model, UserMixin):
    userID  = db.Column(db.Integer, primary_key=True)
    employeeID = db.Column(db.Integer, db.ForeignKey('employee.employeeID'))
    passwordHash = db.Column(db.String(128), nullable= True) #nullable so we can create hash before storing
    email = db.Column(db.String(50), unique=True, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    employee = db.relationship('Employee', backref = 'user')
    
    def get_id(self):
        """Override get_id to use userID as the identifier."""
        return str(self.userID)

    def set_password(self, password):
        """Hash the password and store it."""
        self.passwordHash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.passwordHash, password)


class ShiftAssignment(db.Model):
    assignmentID = db.Column(db.Integer, primary_key=True)
    shiftID = db.Column(db.Integer, db.ForeignKey('shift.shiftID'))
    employeeID = db.Column(db.Integer, db.ForeignKey('employee.employeeID'))
    employee = db.relationship('Employee', backref='assignments')
    shift = db.relationship('Shift', backref='assignments')


class Employee(db.Model):
    employeeID = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    minHours = db.Column(db.Integer, nullable=False)
    maxHours = db.Column(db.Integer, nullable=False)
    gradYear = db.Column(db.Integer)
    unavailabilities = db.relationship('Unavailability', backref = 'employee')
   

class Shift(db.Model):
    shiftID = db.Column(db.Integer, primary_key=True)
    shiftStartTime = db.Column(db.DateTime, nullable=False)
    shiftEndTime = db.Column(db.DateTime, nullable=False)
    
    

class Unavailability(db.Model):
    unavailabilityID = db.Column(db.Integer, primary_key=True)
    employeeID = db.Column(db.Integer, db.ForeignKey('employee.employeeID'))
    unavailableStartTime = db.Column(db.DateTime)
    unavailableEndTime = db.Column(db.DateTime)

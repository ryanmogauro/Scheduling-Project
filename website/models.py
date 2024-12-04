from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from website import db
from datetime import datetime


class User(db.Model, UserMixin):
    userID  = db.Column(db.Integer, primary_key=True)
    employeeID = db.Column(db.Integer, db.ForeignKey('employee.employeeID'))
    passwordHash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    employee = db.relationship('Employee', backref = 'user')
    
    def get_id(self):
        """Override get_id to use userID as the identifier."""
        return str(self.userID)

class Employee(db.Model):
    employeeID = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    minHours = db.Column(db.Integer, default=4)
    maxHours = db.Column(db.Integer, default=12)
    gradYear = db.Column(db.Integer, default=2025)
    wage = db.Column(db.Numeric(10, 2), nullable=False, default=13.50)
    unavailabilities = db.relationship('Unavailability', backref = 'employee')
    notifications = db.relationship('Notification', backref='employee')
    isAdmin = db.Column(db.Boolean, nullable=False, default=False)

class ShiftAssignment(db.Model):
    assignmentID = db.Column(db.Integer, primary_key=True)
    shiftID = db.Column(db.Integer, db.ForeignKey('shift.shiftID'))
    employeeID = db.Column(db.Integer, db.ForeignKey('employee.employeeID'))
    employee = db.relationship('Employee', backref='assignments')
    shift = db.relationship('Shift', backref='assignments')

class Shift(db.Model):
    shiftID = db.Column(db.Integer, primary_key=True)
    shiftStartTime = db.Column(db.DateTime, nullable=False)
    shiftEndTime = db.Column(db.DateTime, nullable=False)
      
class Unavailability(db.Model):
    unavailabilityID = db.Column(db.Integer, primary_key=True)
    employeeID = db.Column(db.Integer, db.ForeignKey('employee.employeeID'), nullable=False)
    unavailableStartTime = db.Column(db.DateTime)
    unavailableEndTime = db.Column(db.DateTime)

class Event(db.Model):
    eventID = db.Column(db.Integer, primary_key=True)
    eventHost = db.Column(db.String(100), nullable = False)
    eventName = db.Column(db.String(100), nullable=False)
    eventStartTime = db.Column(db.DateTime, nullable=False)
    eventEndTime = db.Column(db.DateTime, nullable=False)
    eventDescription = db.Column(db.String(255), nullable=True)

class Notification(db.Model):
    notificationID = db.Column(db.Integer, primary_key=True)
    employeeID = db.Column(db.Integer, db.ForeignKey('employee.employeeID'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    hasRead = db.Column(db.Boolean, default=False)
    sendTime = db.Column(db.DateTime, default=datetime.utcnow)
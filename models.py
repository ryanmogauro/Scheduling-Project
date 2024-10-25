from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    userID  = db.Column(db.Integer, primary_key=True)
    employeeID = db.Column(db.Integer, db.Foreign_Key('employee'))
    username = db.Column(db.String(50), unique = True, nullable=False)
    passwordHash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(50), unique=True)
    isActive = db.Column(db.Boolean, default=True)
    employee = db.relationship('Employee', backref = 'user')


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
    shifts = db.relationship('ShiftAssignment', backref = 'employee')
    unavailabilities = db.relationship('Unavailability', backref = 'employee')
   

class Shift(db.Model):
    shiftID = db.Column(db.Integer, primary_key=True)
    shiftStartTime = db.Column(db.DateTime, nullable=False)
    shiftEndTime = db.Column(db.DateTime, nullable=False)
    shiftAssignments = db.relationship('ShiftAssignment', backref='shift')
    
    

class Unavailability(db.Model):
    unavailabilityID = db.Column(db.Integer, primary_key=True)
    employeeID = db.Column(db.Integer, db.ForeignKey('employee.employeeID'))
    unavailableStartTime = db.Column(db.DateTime)
    unavailableEndTime = db.Column(db.DateTime)
    employee = db.relationship('Employee', backref='unavailabilities')

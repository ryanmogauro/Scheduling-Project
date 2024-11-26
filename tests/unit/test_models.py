from website.models import User, Employee, Shift, ShiftAssignment, Unavailability
from website import db
from datetime import datetime

def test_user_set_password():
    user = User(email="test@colby.edu")
    user.set_password("password")

    assert user.passwordHash is not None
    assert user.passwordHash != "password"


def test_user_check_password():
    user = User(email="test@colby.edu")
    user.set_password("password")

    assert user.check_password("password")  
    assert not user.check_password("wrongpassword")


def test_employee_creation():
    employee = Employee(
        firstName="first",
        lastName="last",
        minHours=20,
        maxHours=40,
        gradYear=2024
    )

    assert employee.firstName == "first"
    assert employee.lastName == "last"
    assert employee.minHours == 20
    assert employee.maxHours == 40
    assert employee.gradYear == 2024


def test_shift_creation():
    shift = Shift(
        shiftStartTime=datetime(2024, 11, 26, 9, 0),
        shiftEndTime=datetime(2024, 11, 26, 17, 0)
    )

    assert shift.shiftStartTime == datetime(2024, 11, 26, 9, 0)
    assert shift.shiftEndTime == datetime(2024, 11, 26, 17, 0)


def test_shift_assignment_relationship():
    employee = Employee(
        firstName="first",
        lastName="last",
        minHours=15,
        maxHours=30
    )
    shift = Shift(
        shiftStartTime=datetime(2024, 11, 26, 14, 0),
        shiftEndTime=datetime(2024, 11, 26, 18, 0)
    )
    assignment = ShiftAssignment(employee=employee, shift=shift)

    assert assignment.employee == employee
    assert assignment.shift == shift
    assert employee.assignments[0] == assignment
    assert shift.assignments[0] == assignment


def test_unavailability_creation():
    employee = Employee(
        firstName="first",
        lastName="last",
        minHours=10,
        maxHours=25
    )
    unavailability = Unavailability(
        employee=employee,
        unavailableStartTime=datetime(2024, 11, 26, 12, 0),
        unavailableEndTime=datetime(2024, 11, 26, 16, 0)
    )

    assert unavailability.employee == employee
    assert unavailability.unavailableStartTime == datetime(2024, 11, 26, 12, 0)
    assert unavailability.unavailableEndTime == datetime(2024, 11, 26, 16, 0)

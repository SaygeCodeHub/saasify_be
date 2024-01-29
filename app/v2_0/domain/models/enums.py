"""Enums"""

from enum import Enum as PyEnum


class ActivityStatus(PyEnum):
    """States the activity of a user"""
    INACTIVE = 0
    ACTIVE = 1


class RolesEnum(PyEnum):
    """Enum for roles of an employee in a company"""
    OWNER = 0
    MANAGER = 1
    ACCOUNTANT = 2
    EMPLOYEE = 3


class LeaveStatus(PyEnum):
    """States the current status of an applied leave"""
    REJECTED = 0
    PENDING = 1
    ACCEPTED = 2


class LeaveType(PyEnum):
    """States the type of leave"""
    CASUAL = 0
    MEDICAL = 1

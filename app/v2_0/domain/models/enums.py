"""Enums"""

from enum import Enum as PyEnum


class ActivityStatus(PyEnum):
    """States the activity of a user"""
    INACTIVE = 0
    ACTIVE = 1


class DesignationEnum(PyEnum):
    """Enum for designations of an employee in a company"""
    OWNER = 0
    MANAGER = 1
    EMPLOYEE = 2


class LeaveStatus(PyEnum):
    """States the current status of an applied leave"""
    REJECTED = 0
    PENDING = 1
    ACCEPTED = 2


class LeaveType(PyEnum):
    """States the type of leave"""
    CASUAL = 0
    MEDICAL = 1


class Modules(PyEnum):
    """States the modules"""
    HR = 0
    POS = 1
    INVENTORY = 2
    INVOICING = 3


class Features(PyEnum):
    HR_FEATURE_1 = 0
    POS_FEATURE_1 = 1
    INVENTORY_FEATURE_1 = 2
    INVOICING_FEATURE_1 = 3

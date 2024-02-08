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
    ACCOUNTING = 1
    INVOICE = 2
    INVENTORY = 3
    POS = 4


class Features(PyEnum):
    HR_MARK_ATTENDANCE = 0.0
    HR_PENDING_APPROVAL = 0.1
    HR_TOTAL_EMPLOYEES = 0.2
    HR_SALARY_ROLLOUT = 0.3
    HR_ADD_NEW_EMPLOYEE = 0.4
    HR_VIEW_ALL_EMPLOYEES = 0.5
    HR_APPLY_LEAVES = 0.6
    HR_MY_LEAVES = 0.7
    HR_TIMESHEET = 0.8
    HR_FEATURE_1 = 0.9

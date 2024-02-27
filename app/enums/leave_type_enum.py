from enum import Enum as PyEnum


class LeaveType(PyEnum):
    """States the type of leave"""
    CASUAL = 0
    MEDICAL = 1

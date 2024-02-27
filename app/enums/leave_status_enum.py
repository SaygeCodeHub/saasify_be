from enum import Enum as PyEnum


class LeaveStatus(PyEnum):
    """States the current status of an applied leave"""
    REJECTED = 0
    PENDING = 1
    APPROVED = 2
    WITHDRAWN = 3

"""Enum - Activity Status"""

from enum import Enum as PyEnum


class ActivityStatus(PyEnum):
    """States the activity of a user"""
    INACTIVE = 0
    ACTIVE = 1

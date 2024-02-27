from enum import Enum as PyEnum


class DesignationEnum(PyEnum):
    """Enum for designations of an employee in a company"""
    OWNER = 0
    MANAGER = 1
    EMPLOYEE = 2

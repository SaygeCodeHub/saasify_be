from enum import Enum as PyEnum


class Features(PyEnum):
    HR_MARK_ATTENDANCE = 0.0
    HR_PENDING_APPROVAL = 0.1
    HR_SALARY_ROLLOUT = 0.2
    HR_ADD_NEW_EMPLOYEE = 0.3
    HR_VIEW_ALL_EMPLOYEES = 0.4
    HR_APPLY_LEAVES = 0.5
    HR_MY_LEAVES = 0.6
    HR_TIMESHEET = 0.7
    HR_SHIFT_MANAGEMENT = 0.8
    HR_ADD_ANNOUNCEMENT = 0.9
    HR_ADD_TASK = 0.11
    HR_VIEW_ALL_TASKS = 0.12
    POS_ADD_CATEGORY = 4.0
    POS_VIEW_CATEGORIES = 4.1
    POS_ADD_PRODUCT = 4.2
    POS_VIEW_PRODUCTS = 4.3
    POS_INVENTORY = 4.4
    POS_POS = 4.5

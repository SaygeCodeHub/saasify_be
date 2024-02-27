from enum import Enum as PyEnum


class TaskStatus(PyEnum):
    PENDING = 0
    DONE = 1
    CLOSED = 2

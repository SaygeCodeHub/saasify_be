"""Schemas for model - Tasks"""
from datetime import date, datetime

from pydantic import BaseModel

from app.v2_0.domain.models.enums import TaskPriority
from app.v2_0.domain.schemas.modifier_schemas import Modifier


class Data(BaseModel):
    id: int
    name: str


class TasksSchema(BaseModel):
    title: str
    task_description: str
    due_date: date
    priority: TaskPriority


class AssignTask(TasksSchema):
    monitored_by: int = None
    assigned_to: int
    company_id: int = None
    branch_id: int = None


class GetTasksAssignedToMe(TasksSchema):
    assigned_by: Data
    task_status: str
    task_id: int


class GetTasksAssignedByMe(TasksSchema):
    assigned_to: Data
    task_status: str
    task_id: int


class UpdateTask(Modifier):
    title: str
    monitored_by: int
    task_id: int
    completion_date: datetime
    task_status: str

"""Schemas for model - Tasks"""
from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.v2_0.HRMS.domain.schemas.modifier_schemas import Modifier
from app.v2_0.enums import TaskPriority


class Data(BaseModel):
    id: Optional[int] = None
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
    comment: Optional[str] = None


class GetTasksAssignedByMe(TasksSchema):
    assigned_to: Data
    task_status: str
    task_id: int
    comment: Optional[str] = None


class UpdateTask(Modifier):
    title: str
    monitored_by: int
    task_id: int
    task_status: Optional[str] = None
    comment: Optional[str] = None


class EditTask(AssignTask):
    title: str
    task_description: str
    due_date: date
    priority: TaskPriority
    task_id: int
    comment: Optional[str] = None
    task_status: str = None
    assigned_to: int
    company_id: int = None
    branch_id: int = None
    monitored_by: int

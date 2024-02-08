"""Schemas for model - Tasks"""
from datetime import date

from pydantic import BaseModel

from app.v2_0.domain.models.enums import TaskPriority, TaskStatus
from app.v2_0.domain.schemas.modifier_schemas import Modifier


class AssignerData(BaseModel):
    id: int
    name: str


class TasksSchema(BaseModel):
    title: str
    task_description: str
    due_date: date
    priority: TaskPriority


class AssignTask(Modifier,TasksSchema):
    monitored_by: int = None
    assigned_to: int
    company_id: int = None
    branch_id: int = None


class GetMyTasks(TasksSchema):
    assigned_by: AssignerData
    task_status: str

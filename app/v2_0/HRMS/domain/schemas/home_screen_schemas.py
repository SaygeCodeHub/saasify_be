"""Schemas for Home screen API"""
from typing import List

from pydantic import BaseModel

from app.v2_0.enums import Features, Modules
from app.v2_0.HRMS.domain.schemas.announcement_schemas import GetAnnouncements
from app.v2_0.HRMS.domain.schemas.branch_schemas import GetBranch
from app.v2_0.HRMS.domain.schemas.module_schemas import ModulesMap, AvailableModulesMap
from app.v2_0.HRMS.domain.schemas.task_schemas import GetTasksAssignedToMe, GetTasksAssignedByMe


class HomeScreenApiResponse(BaseModel):
    branches: List[GetBranch]
    accessible_modules: List[ModulesMap]
    available_modules: List[AvailableModulesMap]
    tasks_assigned_to_me: List[GetTasksAssignedToMe]
    tasks_assigned_by_me: List[GetTasksAssignedByMe]
    announcements: List[GetAnnouncements]
    geo_fencing: bool


class IteratedBranchSettings(BaseModel):
    accessible_features: List[Features]
    accessible_modules: List[Modules]
    geo_fencing: bool


class Salaries(BaseModel):
    basic_salary: float
    deduction: float

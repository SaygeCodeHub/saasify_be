"""Schemas for Home screen API"""
from typing import List

from pydantic import BaseModel

from app.v2_0.domain.schemas.branch_schemas import GetBranch


class HomeScreenAPI(BaseModel):
    branches: List[GetBranch]
    total_employees: int
    pending_leaves: int
    monthly_salary_rollout: float


class Salaries(BaseModel):
    basic_salary: float
    deduction: float

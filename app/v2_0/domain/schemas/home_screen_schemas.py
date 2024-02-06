"""Schemas for Home screen API"""
from typing import List

from pydantic import BaseModel

from app.v2_0.domain.schemas.branch_schemas import GetBranch
from app.v2_0.domain.schemas.leaves_schemas import GetPendingLeaves


class HomeScreenAPI(BaseModel):
    branches: List[GetBranch]
    pending_leaves: int
    monthly_salary_rollout: float


class Salaries(BaseModel):
    salary: float
    deduction: float

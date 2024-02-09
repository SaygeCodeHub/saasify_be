"""Schemas for Home screen API"""
from typing import List

from pydantic import BaseModel

from app.v2_0.domain.models.enums import Features, Modules
from app.v2_0.domain.schemas.branch_schemas import GetBranch
from app.v2_0.domain.schemas.module_schemas import ModulesMap, FeaturesMap


class HomeScreenApiResponse(BaseModel):
    branches: List[GetBranch]
    accessible_modules: List[ModulesMap]
    accessible_features: List[FeaturesMap]
    geo_fencing: bool


class IteratedBranchSettings(BaseModel):
    accessible_features:List[Features]
    accessible_modules: List[Modules]
    geo_fencing: bool


class Salaries(BaseModel):
    basic_salary: float
    deduction: float

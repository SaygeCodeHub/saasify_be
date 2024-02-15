"""Schemas for Employee"""
from typing import Optional, List

from pydantic import BaseModel

from app.v2_0.enums import DesignationEnum
from app.v2_0.HRMS.domain.schemas.modifier_schemas import Modifier
from app.v2_0.HRMS.domain.schemas.module_schemas import ModulesMap
from app.v2_0.HRMS.domain.schemas.user_schemas import UpdateUser


class GetEmployees(BaseModel):
    employee_id: Optional[int] = None
    name: str
    user_contact: Optional[int]
    designations: List[str]
    user_email: str
    current_address: Optional[str]


class InviteEmployee(Modifier):
    user_email: Optional[str] = None
    designations: List[DesignationEnum]
    approvers: List = None
    accessible_modules: Optional[List[ModulesMap]] = None


class UpdateEmployee(UpdateUser):
    first_name: str
    last_name: str


class GetEmployeeSalaries(BaseModel):
    name: str
    designations: List[str]
    resultant_salary: float

"""Schemas for Employee"""
from typing import Optional, List

from pydantic import BaseModel

from app.v2_0.domain.models.enums import DesignationEnum, Modules
from app.v2_0.domain.schemas.modifier_schemas import Modifier
from app.v2_0.domain.schemas.user_schemas import UpdateUser


class GetEmployees(BaseModel):
    name: str
    user_contact: Optional[int]
    designations: List[DesignationEnum]
    user_email: str
    current_address: Optional[str]


class InviteEmployee(Modifier):
    user_email: Optional[str] = None
    designations: List[DesignationEnum]
    approvers: List = None
    # accessible_features: List[Features] = None
    accessible_moduless: List[Modules] = None


class UpdateEmployee(UpdateUser):
    first_name: str
    last_name: str

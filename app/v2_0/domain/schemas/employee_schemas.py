"""Schemas for Employee"""
from typing import Optional, List

from pydantic import BaseModel

from app.v2_0.domain.models.enums import RolesEnum
from app.v2_0.domain.schemas.modifier_schemas import Modifier
from app.v2_0.domain.schemas.user_schemas import UpdateUser


class GetEmployees(BaseModel):
    name: str
    user_contact: Optional[int]
    roles: List[RolesEnum]
    user_email: str
    current_address: Optional[str]


class InviteEmployee(Modifier):
    user_email: Optional[str] = None
    roles: List[RolesEnum]
    approvers: List = None


class UpdateEmployee(UpdateUser):
    first_name: str
    last_name: str

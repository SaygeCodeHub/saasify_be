"""Schemas for Branches"""
from datetime import date, datetime
from typing import List

from pydantic import BaseModel

from app.v2_0.domain.models.enums import ActivityStatus
from app.v2_0.domain.schemas.modifier_schemas import Modifier
from app.v2_0.domain.schemas.module_schemas import ModuleInfoResponse


class UpdateBranch(Modifier):
    company_id: int = None
    branch_name: str
    branch_address: str = None
    branch_currency: str = None
    activity_status: ActivityStatus = "ACTIVE"
    is_head_quarter: bool = None
    branch_contact: int = None
    location: str = None
    pincode: int = None,
    longitude: float = None
    latitude: float = None


class AddBranch(UpdateBranch):
    """Contains all the fields that will be accessible to all objects of type - 'Branch' """
    created_at: date = datetime.now()


class GetBranch(BaseModel):
    branch_name: str
    branch_id: int
    activity_status: ActivityStatus
    branch_address: str
    is_head_quarter: bool
    branch_contact: int
    company_id: int
    branch_currency: str


class CreateBranchResponse(BaseModel):
    branch_name: str
    branch_id: int
    modules: List[ModuleInfoResponse]

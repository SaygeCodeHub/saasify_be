"""Schemas for Branches"""
from datetime import date, datetime
from typing import List

from pydantic import BaseModel

from app.v2_0.domain.models.enums import ActivityStatus, Modules, Features
from app.v2_0.domain.schemas.modifier_schemas import Modifier


class UpdateBranch(Modifier):
    company_id: int = None
    branch_name: str
    branch_address: str = ""
    branch_currency: str = ""
    activity_status: ActivityStatus = ActivityStatus.ACTIVE
    is_head_quarter: bool = None
    branch_contact: int = None
    location: str = ""
    pincode: int = None
    longitude: float = None
    latitude: float = None


class AddBranch(UpdateBranch):
    """Contains all the fields that will be accessible to all objects of type - 'Branch' """
    created_at: date = datetime.now()


class GetBranch(BaseModel):
    branch_name: str
    branch_id: int



class CreateBranchResponse(BaseModel):
    branch_name: str
    branch_id: int
    # modules: Optional[List[Modules]]



 # accessible_modules: List[Modules]
 #    accessible_features: List[Features]
 #    geo_fencing: bool
"""Schemas for Branch Settings"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.v2_0.domain.schemas.modifier_schemas import Modifier


class GetBranchSettings(BaseModel):
    time_in: Optional[datetime]
    time_out: Optional[datetime]
    timezone: Optional[datetime]
    currency: Optional[str]
    default_approver: Optional[str]
    overtime_rate: Optional[float]
    overtime_rate_per: Optional[str]
    total_medical_leaves: Optional[int]
    total_casual_leaves: Optional[int]
    geo_fencing: bool


class UpdateBranchSettings(Modifier):
    time_in: Optional[datetime]
    time_out: Optional[datetime]
    timezone: Optional[datetime] = None
    currency: Optional[str] = ""
    default_approver: int
    working_days: Optional[int]
    total_medical_leaves: Optional[int] = 12
    total_casual_leaves: Optional[int] = 3
    overtime_rate: Optional[float] = None
    overtime_rate_per: Optional[str]


class BranchSettingsSchema(UpdateBranchSettings):
    setting_id: int
    branch_id: int
    company_id: int
    is_hq_settings: bool
    created_at: date = datetime.now()

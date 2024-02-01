"""Schemas for Branch Settings"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.v2_0.domain.schemas.modifier_schemas import Modifier


class GetBranchSettings(BaseModel):
    time_in: Optional[str]
    time_out: Optional[str]
    timezone: Optional[str]
    currency: Optional[str]
    default_approver: Optional[int]
    overtime_rate: Optional[float]
    overtime_rate_per: Optional[str]
    total_medical_leaves: Optional[int]
    total_casual_leaves: Optional[int]


class UpdateBranchSettings(Modifier):
    time_in: Optional[str] = "9:30"
    time_out: Optional[str] = "6:30"
    timezone: Optional[str] = None
    currency: Optional[str] = None
    default_approver: int
    working_days: Optional[int]
    total_medical_leaves: Optional[int] = 12
    total_casual_leaves: Optional[int] = 3
    overtime_rate: Optional[float] = None
    overtime_rate_per: Optional[str] = "HOUR"


class BranchSettingsSchema(UpdateBranchSettings):
    setting_id: int
    branch_id: int
    company_id: int
    is_hq_settings: bool
    created_at: date = datetime.now()

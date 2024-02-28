"""Schemas for Branch Settings"""
from datetime import date, datetime
from typing import Optional, Union

from pydantic import BaseModel

from app.v2_0.HRMS.domain.schemas.leaves_schemas import ApproverData
from app.v2_0.HRMS.domain.schemas.modifier_schemas import Modifier


class GetBranchSettings(BaseModel):
    time_in: Optional[Union[datetime, str]]
    time_out: Optional[Union[datetime, str]]
    timezone: Optional[Union[datetime, str]] = None
    currency: Optional[str] = ""
    default_approver: Optional[ApproverData]
    working_days: Optional[int]
    total_medical_leaves: Optional[Union[int, str]] = 12
    total_casual_leaves: Optional[Union[int, str]] = 3
    overtime_rate: Optional[Union[float, str]] = None
    overtime_rate_per: Optional[str]
    branch_address: Optional[str] = ""
    pincode: Optional[Union[int, str]] = None
    longitude: Optional[Union[float, str]] = None
    latitude: Optional[Union[float, str]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.time_in == "":
            self.time_in = None
        if self.time_out == "":
            self.time_out = None
        if self.timezone == "":
            self.timezone = None
        if self.overtime_rate == "":
            self.overtime_rate = None
        if self.pincode == "":
            self.pincode = None
        if self.longitude == "":
            self.longitude = None
        if self.latitude == "":
            self.latitude = None


class UpdateBranchSettings(Modifier):
    time_in: Optional[Union[datetime, str]]
    time_out: Optional[Union[datetime, str]]
    timezone: Optional[Union[datetime, str]] = None
    currency: Optional[str] = ""
    default_approver: int
    working_days: Optional[Union[int, str]] = None
    total_medical_leaves: Optional[Union[int, str]] = 12
    total_casual_leaves: Optional[Union[int, str]] = 3
    overtime_rate: Optional[Union[float, str]] = None
    overtime_rate_per: Optional[str]
    branch_address: Optional[str] = ""
    pincode: Optional[Union[int, str]] = None
    longitude: Optional[Union[float, str]] = None
    latitude: Optional[Union[float, str]] = None
    geo_fencing: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.time_in == "":
            self.time_in = None
        if self.time_out == "":
            self.time_out = None
        if self.timezone == "":
            self.timezone = None
        if self.overtime_rate == "":
            self.overtime_rate = None
        if self.pincode == "":
            self.pincode = None
        if self.longitude == "":
            self.longitude = None
        if self.latitude == "":
            self.latitude = None
        if self.working_days == "":
            self.working_days = None


class BranchSettingsSchema(UpdateBranchSettings):
    setting_id: int
    branch_id: int
    company_id: int
    is_hq_settings: bool
    created_at: date = datetime.now()

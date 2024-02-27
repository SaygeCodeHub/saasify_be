"""Schemas for Leaves"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from app.enums.leave_status_enum import LeaveStatus
from app.enums.leave_type_enum import LeaveType
from app.v2_0.HRMS.domain.schemas.modifier_schemas import Modifier


class ApproverData(BaseModel):
    id: int
    approver_name: str


class LoadApplyLeaveScreen(BaseModel):
    casual_leaves: Optional[int]
    medical_leaves: Optional[int]
    approvers: List[ApproverData]


class ApplyLeaveResponse(BaseModel):
    leave_id: int
    leave_status: str
    is_leave_approved: bool
    comment: Optional[str]


class UpdateLeave(Modifier):
    leave_id: int
    comment: Optional[str] = None
    leave_status: LeaveStatus = None
    is_leave_approved: bool


class GetPendingLeaves(BaseModel):
    leave_id: int
    user_id: int
    name: str
    leave_type: str
    leave_reason: str
    start_date: date
    end_date: date
    approvers: List


class GetLeaves(BaseModel):
    user_id: int
    leave_type: str
    leave_id: int
    leave_reason: str
    start_date: date
    end_date: date
    approvers: List
    leave_status: str
    comment: Optional[str] = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ensure_optional_fields()

    def ensure_optional_fields(self):
        # Ensure all optional fields have default values
        for field in self.__annotations__:
            if field in self.__dict__ and self.__dict__[field] is None:
                if self.__annotations__[field] == str:
                    setattr(self, field, "")
                if self.__annotations__[field] == Optional[str]:
                    setattr(self, field, "")
                elif self.__annotations__[field] == List:
                    setattr(self, field, [])
                elif self.__annotations__[field] == dict:
                    setattr(self, field, {})
                else:
                    setattr(self, field, None)


class ApplyLeave(Modifier):
    company_id: int = None
    branch_id: int = None
    user_id: int = None
    leave_type: LeaveType
    leave_reason: str
    start_date: date
    end_date: date
    approvers: List
    leave_status: LeaveStatus = "PENDING"
    is_leave_approved: bool = False


class FetchAllLeavesResponse(BaseModel):
    pending_leaves: List[GetPendingLeaves]
    my_leaves: List[GetLeaves]

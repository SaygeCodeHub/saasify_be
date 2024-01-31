"""Schemas for Leaves"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from app.v2_0.domain.models.enums import LeaveStatus, LeaveType
from app.v2_0.domain.schemas.modifier_schemas import Modifier


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
    comment: str
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

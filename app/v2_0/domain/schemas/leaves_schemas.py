"""Schemas for Leaves"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from app.v2_0.domain.models.enums import LeaveStatus, LeaveType
from app.v2_0.domain.schemas.modifier_schemas import Modifier


class LoadApplyLeaveScreen(BaseModel):
    casual_leaves: Optional[int]
    medical_leaves: Optional[int]
    approvers: List[int]


class ApplyLeaveResponse(BaseModel):
    leave_id: int
    leave_status: LeaveStatus
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
    leave_type: LeaveType
    leave_reason: str
    start_date: date
    end_date: date
    approvers: List


class GetLeaves(BaseModel):
    company_id: int
    branch_id: int
    user_id: int
    leave_type: LeaveType
    leave_id: int
    leave_reason: str
    start_date: date
    end_date: date
    approvers: List
    leave_status: LeaveStatus


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
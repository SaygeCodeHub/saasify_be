"""Schemas for different models are written here"""
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel

from app.v2_0.domain.models import ActivityStatus, RolesEnum, LeaveType, LeaveStatus


class Modifier(BaseModel):
    """Contains all the fields that will be inherited by other schemas """
    modified_on: date = datetime.now()
    modified_by: int = -1


"""----------------------------------------------Branch Settings related schemas-------------------------------------------------------------------"""


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
    total_medical_leaves: Optional[int] = 0
    total_casual_leaves: Optional[int] = 0
    overtime_rate: Optional[float] = None
    overtime_rate_per: Optional[str] = "HOUR"


class BranchSettings(UpdateBranchSettings):
    setting_id: int
    branch_id: int
    company_id: int
    is_hq_settings: bool
    created_at: date = datetime.now()


"""----------------------------------------------Branch related Schemas-------------------------------------------------------------------"""


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


"""----------------------------------------------Company related Schemas-------------------------------------------------------------------"""


class UpdateCompany(Modifier):
    company_name: str
    company_domain: str = None
    company_logo: str = None
    company_email: str = None
    services: str = None
    owner: int = None
    activity_status: ActivityStatus = "ACTIVE"


class AddCompany(AddBranch, UpdateCompany):
    """Contains all the fields that will be accessible to all objects of type - 'Company' """
    onboarding_date: date = datetime.now()


class GetCompany(BaseModel):
    company_id: int
    company_name: Optional[str]
    owner: Optional[int]
    activity_status: Optional[ActivityStatus]


"""----------------------------------------------User related Schemas-------------------------------------------------------------------"""


class LoginResponse(BaseModel):
    user_id: int
    name: str
    company: List


class AddUser(Modifier):
    """Contains all the fields that will be accessible to all objects of type - 'User' """
    first_name: str = None
    last_name: str = None
    password: str
    user_email: str
    change_password_token: str = None
    medical_leaves: Optional[int] = 0
    casual_leaves: Optional[int] = 0
    activity_status: ActivityStatus = "ACTIVE"


class GetUser(BaseModel):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    middle_name: Optional[str] = None
    user_id: int
    user_contact: Optional[int] = None
    alternate_contact: Optional[int] = None
    user_image: Optional[str] = None
    user_email: str
    roles: List[RolesEnum] = None
    user_birthdate: Optional[date] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None


class UpdateUser(Modifier):
    first_name: str = ""
    last_name: str = ""
    user_birthdate: date = None
    activity_status: ActivityStatus = None
    user_image: str = "Image"
    user_contact: int = None
    alternate_contact: int = None
    age: int = None
    middle_name: str = None
    gender: str = None
    nationality: str = None
    marital_status: str = None
    current_address: str = None
    permanent_address: str = None
    city: str = None
    state: str = None
    pincode: Optional[int] = None


"""----------------------------------------------Employee related Schemas-------------------------------------------------------------------"""


class GetEmployees(BaseModel):
    name: str
    user_contact: Optional[int]
    roles: List[RolesEnum]
    user_email: str
    current_address: Optional[str]


class InviteEmployee(Modifier):
    user_email: str
    roles: List[RolesEnum]
    approvers: List = None


class UpdateEmployee(UpdateUser):
    first_name: str
    last_name: str


"""----------------------------------------------Leaves related Schemas-------------------------------------------------------------------"""


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


"""----------------------------------------------Approver related Schemas-------------------------------------------------------------------"""


class AddApprover(BaseModel):
    approvers: List


"""----------------------------------------------Utility Schemas-------------------------------------------------------------------"""


class Credentials(BaseModel):
    """Used to get the credentials of an individual"""
    email: str
    password: str


class PwdResetToken(BaseModel):
    """Used to get the JSON object for pwd reset token"""
    token: str
    user_email: str


class JSONObject(BaseModel):
    """Used to get selected json fields from FE"""
    email: Optional[str] = None
    pwd: Optional[str] = None


class UserDataResponse(BaseModel):
    branch_id: int
    branch_name: str
    roles: List[RolesEnum]

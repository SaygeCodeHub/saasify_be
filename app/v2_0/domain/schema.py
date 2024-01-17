"""Schemas for different models are written here"""
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel

from app.v2_0.domain.models import ActivityStatus, RolesEnum


class Modifier(BaseModel):
    """Contains all the fields that will be inherited by other schemas """
    modified_on: date = datetime.now()
    modified_by: int = -1


class GetCompanySettings(BaseModel):
    time_in: Optional[str]
    time_out: Optional[str]
    timezone: Optional[str]
    currency: Optional[str]
    default_approver: Optional[int]
    overtime_rate: Optional[float]
    overtime_rate_per: Optional[str]


class UpdateCompanySettings(Modifier):
    time_in: Optional[str] = "9:30"
    time_out: Optional[str] = "6:30"
    timezone: Optional[str] = None
    currency: Optional[str] = None
    default_approver: int
    working_days: Optional[int]
    overtime_rate: Optional[float] = None
    overtime_rate_per: Optional[str] = "HOUR"


class CompanySettings(UpdateCompanySettings):
    setting_id: int
    branch_id: int
    company_id: int
    is_hq_settings: bool
    created_at: date = datetime.now()


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
    longitude: str = None
    latitude: str = None


class AddBranch(UpdateBranch):
    """Contains all the fields that will be accessible to all objects of type - 'Branch' """
    created_at: date = datetime.now()


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


class AddUser(Modifier):
    """Contains all the fields that will be accessible to all objects of type - 'User' """
    first_name: str = None
    last_name: str = None
    password: str
    user_email: str
    user_contact: int = None
    user_birthdate: date = None
    user_image: str = "Image"
    activity_status: ActivityStatus = "ACTIVE"
    change_password_token: str = None


class InviteEmployee(Modifier):
    user_email: str
    role: RolesEnum


class UpdateUser(Modifier):
    first_name: str
    last_name: str
    user_birthdate: date = None
    activity_status: ActivityStatus = None
    user_image: str = "Image"
    user_contact: int = None


class UpdateEmployee(UpdateUser):
    first_name: str
    last_name: str


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


class GetUser(BaseModel):
    first_name: str
    last_name: str
    user_id: int
    user_email: str
    user_contact: int
    user_image: str


class GetCompany(BaseModel):
    company_id: int
    company_name: Optional[str]
    company_logo: Optional[str]
    company_email: Optional[str]


class GetBranch(BaseModel):
    branch_name: str
    branch_id: int

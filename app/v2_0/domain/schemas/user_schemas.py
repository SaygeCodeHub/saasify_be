"""Schemas for User"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from app.v2_0.domain.models.enums import ActivityStatus, DesignationEnum, Features, Modules
from app.v2_0.domain.schemas.modifier_schemas import Modifier


class LoginResponse(BaseModel):
    user_id: int
    name: str
    company: List


class PersonalInfo(Modifier):
    first_name: str = ""
    last_name: str = ""
    user_email: str
    user_birthdate: date = None
    activity_status: ActivityStatus = None
    user_image: str = "Image"
    user_contact: int = None
    alternate_contact: int = None
    age: int = None
    middle_name: str = ""
    gender: str = None
    nationality: str = None
    marital_status: str = None
    current_address: str = None
    permanent_address: str = None
    city: str = None
    state: str = None
    pincode: Optional[int] = None


class AadharDetails(BaseModel):
    aadhar_number: Optional[int] = None
    name_as_per_aadhar: str = None
    pan_number: str = None


class PassportDetails(BaseModel):
    passport_num: str = None
    passport_fname: str = None
    passport_lname: str = None
    expiry_date: date = None
    issue_date: date = None
    mobile_number: Optional[int] = None
    current_address: str = None
    permanent_address: str = None


class UserDocumentsSchema(Modifier):
    aadhar: AadharDetails
    passport: PassportDetails


class UserFinanceSchema(Modifier):
    salary: Optional[float] = None


class AddUser(Modifier):
    """Contains all the fields that will be accessible to all objects of type - 'User' """
    first_name: str = ""
    last_name: str = ""
    password: Optional[str] = None
    user_email: str
    change_password_token: str = None
    medical_leaves: Optional[int] = 12
    casual_leaves: Optional[int] = 3
    activity_status: ActivityStatus = "ACTIVE"


class GetUser(BaseModel):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    middle_name: Optional[str] = ""
    user_id: int
    user_contact: Optional[int] = None
    alternate_contact: Optional[int] = None
    user_image: Optional[str] = None
    user_email: str
    designations: List[DesignationEnum] = None
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


class UpdateUser(BaseModel):
    designations: Optional[List[DesignationEnum]] = None
    approvers: Optional[List[int]] = None
    accessible_features: List[Features] = None
    accessible_modules: List[Modules] = None
    personal_info: PersonalInfo
    documents: UserDocumentsSchema
    financial: UserFinanceSchema

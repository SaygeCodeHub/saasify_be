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
    casual_leaves: int = 3
    medical_leaves: int = 12
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


class GetUser(AadharDetails, PassportDetails, UserFinanceSchema):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    middle_name: Optional[str] = ""
    user_id: int
    user_contact: Optional[int] = None
    alternate_contact: Optional[int] = None
    user_image: Optional[str] = None
    user_email: str
    designations: List[DesignationEnum] = None
    approvers: Optional[List[int]] = None
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
    accessible_features: List[Features] = None
    accessible_modules: List[Modules] = None

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


class UpdateUser(BaseModel):
    designations: Optional[List[DesignationEnum]] = None
    approvers: Optional[List[int]] = None
    accessible_features: List[Features] = None
    accessible_modules: List[Modules] = None
    personal_info: PersonalInfo
    documents: UserDocumentsSchema
    financial: UserFinanceSchema


class GetPassportDetails(BaseModel):
    passport_num: Optional[str] = None
    passport_fname: Optional[str] = None
    passport_lname: Optional[str] = None
    expiry_date: Optional[date] = None
    issue_date: Optional[date] = None
    mobile_number: Optional[int] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ensure_optional_fields()

    def ensure_optional_fields(self):
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


class GetAadharDetails(BaseModel):
    aadhar_number: Optional[int] = None
    name_as_per_aadhar: Optional[str] = None
    pan_number: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ensure_optional_fields()

    def ensure_optional_fields(self):
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


class GetPersonalInfo(BaseModel):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    middle_name: Optional[str] = ""
    user_id: int
    user_contact: Optional[int] = None
    alternate_contact: Optional[int] = None
    user_image: Optional[str] = None
    user_email: str
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ensure_optional_fields()

    def ensure_optional_fields(self):
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

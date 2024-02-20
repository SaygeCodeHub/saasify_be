"""Schemas for User"""
from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import BaseModel, ValidationError

from app.v2_0.HRMS.application.utility.app_utility import ensure_optional_fields
from app.v2_0.HRMS.domain.schemas.modifier_schemas import Modifier
from app.v2_0.HRMS.domain.schemas.module_schemas import ModulesMap
from app.v2_0.dto.dto_classes import ResponseDTO
from app.v2_0.enums import ActivityStatus, DesignationEnum, Features, Modules


class LoginResponse(BaseModel):
    user_id: int
    name: str
    company: List


class PersonalInfo(Modifier):
    first_name: str = ""
    last_name: str = ""
    user_email: str
    user_birthdate: Optional[Union[date, str]] = None
    active_status: ActivityStatus = ActivityStatus.ACTIVE
    casual_leaves: Optional[int] = 3
    medical_leaves: Optional[int] = 12
    user_image: str = "Image"
    user_contact: Optional[Union[int, str]] = None
    alternate_contact: Optional[Union[int, str]] = None
    age: Optional[Union[int, str]] = None
    middle_name: str = ""
    gender: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[Union[int, str]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.user_contact == "":
            self.user_contact = None
        if self.alternate_contact == "":
            self.alternate_contact = None
        if self.pincode == "":
            self.pincode = None
        if self.user_birthdate == "":
            self.user_birthdate = None
        if self.age == "":
            self.age = None


class AadharDetails(BaseModel):
    aadhar_number: Optional[Union[int, str]] = None
    name_as_per_aadhar: Optional[str] = None
    pan_number: Optional[Union[int, str]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.aadhar_number == "":
            self.aadhar_number = None
        if self.pan_number == "":
            self.pan_number = None


class PassportDetails(BaseModel):
    passport_num: Optional[str] = None
    passport_fname: Optional[str] = None
    passport_lname: Optional[str] = None
    expiry_date: Optional[date] = None
    issue_date: Optional[date] = None
    mobile_number: Optional[Union[int, str]] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.mobile_number == "":
            self.mobile_number = None
        if self.passport_num == "":
            self.passport_num = None


class UserDocumentsSchema(Modifier):
    aadhar: Optional[AadharDetails]
    passport: Optional[PassportDetails]


class UserFinanceSchema(Modifier):
    fin_id: Optional[int] = None
    user_id: Optional[int] = None
    basic_salary: Optional[Union[float, str]] = 0.0
    BOA: Optional[Union[float, str]] = 0.0
    bonus: Optional[Union[float, str]] = 0.0
    PF: Optional[Union[float, str]] = 0.0
    performance_bonus: Optional[Union[float, str]] = 0.0
    gratuity: Optional[Union[float, str]] = 0.0
    deduction: Optional[Union[float, str]] = 0.0
    fixed_monthly_gross: Optional[Union[float, str]] = 0.0
    total_annual_gross: Optional[Union[float, str]] = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.basic_salary == "":
            self.basic_salary = None
        if self.BOA == "":
            self.BOA = None
        if self.bonus == "":
            self.bonus = None
        if self.PF == "":
            self.PF = None
        if self.performance_bonus == "":
            self.performance_bonus = None
        if self.gratuity == "":
            self.gratuity = None
        if self.deduction == "":
            self.deduction = None
        if self.fixed_monthly_gross == "":
            self.fixed_monthly_gross = None
        if self.total_annual_gross == "":
            self.total_annual_gross = None


class UserBankDetailsSchema(BaseModel):
    bank_detail_id: Optional[int] = None
    bank_name: Optional[str] = None
    account_number: Optional[Union[int, str]] = None
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None
    account_type: Optional[str] = None
    country: Optional[str] = None
    modified_on: Optional[datetime] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.account_number == "":
            self.account_number = None
        if self.ifsc_code == "":
            self.ifsc_code = None


class AddUser(Modifier):
    """Contains all the fields that will be accessible to all objects of type - 'User' """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    user_email: Optional[str] = None
    change_password_token: str = None
    medical_leaves: Optional[int] = 12
    casual_leaves: Optional[int] = 3
    activity_status: ActivityStatus = ActivityStatus.ACTIVE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.first_name == "":
            self.first_name = None
        if self.last_name == "":
            self.last_name = None
        if self.password == "":
            self.password = None
        if self.user_email == "":
            self.user_email = None


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
        ensure_optional_fields(self)


class Financials(BaseModel):
    finances: Optional[UserFinanceSchema]
    bank_details: Optional[UserBankDetailsSchema]


class UserOfficialSchema(Modifier):
    official_id: Optional[int] = None
    doj: Optional[date] = None
    job_confirmation: Optional[bool] = None
    current_location: Optional[str] = None
    department_head: Optional[int] = None
    reporting_manager: Optional[int] = None
    designations: Optional[List[DesignationEnum]] = None
    approvers: Optional[List[int]] = None
    accessible_modules: Optional[List[ModulesMap]] = None


class GetUserOfficialSchema(Modifier):
    official_id: Optional[int] = None
    doj: Optional[date] = None
    job_confirmation: Optional[bool] = None
    current_location: Optional[str] = None
    department_head: Optional[int] = None
    reporting_manager: Optional[int] = None
    designations: Optional[List[DesignationEnum]] = None
    approvers: Optional[List[int]] = None
    accessible_modules: Optional[List[ModulesMap]] = None
    can_edit: Optional[bool] = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ensure_optional_fields(self)


class UpdateUser(BaseModel):
    personal_info: PersonalInfo
    documents: Optional[UserDocumentsSchema]
    financial: Optional[Financials]
    official: Optional[UserOfficialSchema]


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
        ensure_optional_fields(self)


class GetAadharDetails(BaseModel):
    aadhar_number: Optional[int] = None
    name_as_per_aadhar: Optional[str] = None
    pan_number: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ensure_optional_fields(self)


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
        ensure_optional_fields(self)


class GetUserFinanceSchema(Modifier):
    fin_id: Optional[int] = None
    user_id: Optional[int] = None
    basic_salary: Optional[float] = 0.0
    BOA: Optional[float] = 0.0
    bonus: Optional[float] = 0.0
    PF: Optional[float] = 0.0
    performance_bonus: Optional[float] = 0.0
    gratuity: Optional[float] = 0.0
    deduction: Optional[float] = 0.0
    fixed_monthly_gross: Optional[float] = 0.0
    total_annual_gross: Optional[float] = 0.0
    can_edit: Optional[bool] = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ensure_optional_fields(self)


class GetUserBankDetailsSchema(BaseModel):
    bank_detail_id: Optional[int] = None
    bank_name: Optional[str] = None
    account_number: Optional[int] = None
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None
    account_type: Optional[str] = None
    country: Optional[str] = None
    modified_on: Optional[datetime] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ensure_optional_fields(self)

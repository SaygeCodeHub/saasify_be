from typing import Optional, Union
from pydantic import BaseModel, EmailStr


class Companies(BaseModel):
    company_id: Optional[int] | None = None
    company_name: str
    company_password: str | None = None
    company_domain: str
    company_logo: str
    company_email: EmailStr | None = None
    services: str
    company_contact: int
    company_address: str
    white_labelled: bool = True

    class Config:
        from_attributes = True


class CompanyUpdateDetails(BaseModel):
    company_name: str
    company_domain: str
    company_contact: int
    company_address: str
    white_labelled: bool = True

    class Config:
        from_attributes = True


class CompanySignUp(BaseModel):
    signup_credentials: Union[str, int]
    company_id: Optional[str] | None = None
    company_email: str | None = None
    company_contact: int | None = None
    password: str
    company_domain: str | None = " "

    class Config:
        from_attributes = True


class LoginFlow(BaseModel):
    login_credentials: Union[str, int]
    company_contact: int | None = None
    company_email: str | None = None
    employee_contact: int | None = None
    password: str

    class Config:
        from_attributes = True


class NewUsers(BaseModel):
    user_uniqueid: int | None = None
    user_name: str | None = None
    user_contact: str | None = None
    user_birthdate: str | None = None
    user_image: str | None = None
    user_emailId: str | None = None
    user_password: str
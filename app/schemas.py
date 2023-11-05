from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import date


class Companies(BaseModel):
    company_id: Optional[int] | None = None
    company_name: str
    company_domain: str
    company_logo: str | None = None
    company_email: EmailStr | None = None
    services: str | None = None
    owner: str | None = None

    class Config:
        from_attributes = True


class Authentication(BaseModel):
    user_id: str
    user_name: Optional[str] | None = None
    user_contact: int
    user_birthdate: date | None = None

    class Config:
        from_attributes = True


class Branch(BaseModel):
    branch_id: Optional[int] | None = None
    branch_name: str
    branch_contact: int | None = None
    branch_address: str | None = None

    class Config:
        from_attributes = True


class CreateCompany(Companies, Branch):
    pass

    class Config:
        from_attributes = True


class AllBranches(BaseModel):
    branches: List[Branch]

    class Config:
        from_attributes = True

from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import date


class Companies(BaseModel):
    company_id: Optional[int] | None = None
    company_name: str
    company_domain: str
    company_logo: str
    company_email: EmailStr | None = None
    services: str
    company_contact: int
    company_address: str

    class Config:
        from_attributes = True


class Authentication(BaseModel):
    user_id: str
    user_name: Optional[str] | None = None
    user_contact: int
    user_birthdate: date | None = None

    class Config:
        from_attributes = True

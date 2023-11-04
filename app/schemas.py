from typing import Optional, Union, List
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

class ProductInput(BaseModel):
    product_name: str
    brand_name: str
    branch_id: int
    barcode_no: int
    image: List[str]
    description: str
    category_name: str
    variant_cost: float
    discounted_cost: float
    stock: int
    quantity: int
    measuring_unit: str
    is_published: bool

    class Config:
        arbitrary_types_allowed = True

class ProductVariant(BaseModel):
    variant_cost: float
    discounted_cost: float
    stock: int
    quantity: int
    measuring_unit: str
    image: List[str]
    # description: str
    barcode_no: int
    is_published: bool

class ProductEdit(BaseModel):
    branch_id: int
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    description: Optional[str] = None
    category_name: Optional[str] = None
    barcode_no: Optional[int] = None
    variant_cost: Optional[float] = None
    discounted_cost: Optional[float] = None
    stock: Optional[int] = None
    quantity: Optional[int] = None
    measuring_unit: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

class ProductUpdate(BaseModel):
    branch_id: int
    product_name: Optional[str] = None
    description: Optional[str] = None
    category_name: Optional[str] = None


    class Config:
        arbitrary_types_allowed = True
from __future__ import annotations
from app.v1_1.models import ActivityStatus

from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import date, datetime


# class ResponseDTO(BaseModel):
#     status: str
#     data: object
#     message: str
#
#     def __init__(self,status, data, message):
#         self.status = status
#         self.data = data
#         self.message = message


class Modifier(BaseModel):
    modified_by: str = ""
    modified_on: date = datetime.now()


class Companies(Modifier):
    company_id: Optional[int] | None = None
    company_name: str
    company_domain: str
    company_logo: str | None = None
    services: str | None = None
    owner: str | None = None

    class Config:
        from_attributes = True


class Authentication(BaseModel):
    user_id: str
    user_name: Optional[str] | None = None
    user_contact: Optional[Any] = None
    user_email: Optional[str] | None = None
    user_birthdate: date | None = None
    modules: Optional[List[str]] | None = None
    activate_backend: Optional[bool] | None = None

    class Config:
        from_attributes = True


class Branch(Modifier):
    branch_id: Optional[int] | None = None
    company_id: Optional[str] | None = None
    branch_name: str
    branch_contact: int | None = None
    branch_address: str | None = None
    branch_currency: str | None = None
    branch_active: bool | None = True

    class Config:
        from_attributes = True


class EditBranch(BaseModel):
    branch_name: str
    branch_contact: int | None = None
    branch_address: str | None = None
    branch_currency: str | None = None
    branch_active: bool | None = True

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


class GetBranch(BaseModel):
    data: Branch

    class Config:
        from_attributes = True


class AddProducts(BaseModel):
    company_id: Optional[str] | None = None
    branch_id: Optional[int] | None = None
    product_id: Optional[int] | None = None
    category_name: str
    brand_name: str | None = None
    stock: int | None = 0
    product_name: str
    barcode: int
    product_description: str | None = None
    cost: float | None = 0.0
    quantity: int | None = 0
    unit: str | None = None
    images: Optional[List[str]] | None = []
    draft: bool | None = True
    variant_active: Optional[bool] | None = None
    restock_reminder: int | None = 0
    discount_percent: float | None = 0.0
    CGST: float | None = None
    SGST: float | None = None

    class Config:
        from_attributes = True


class EditProduct(AddProducts):
    variant_id: Optional[int] | None = None
    stock_id: Optional[int] | None = None

    class Config:
        from_attributes = True


class DeleteVariants(BaseModel):
    variant_ids: List[int]

    class Config:
        from_attributes = True


class Categories(Modifier):
    category_id: Optional[int] | None = None
    category_name: str
    is_active: bool

    class Config:
        from_attributes = True


class Payment(Modifier):
    branch_id: int = None
    company_id: str = None
    payment_id: Optional[int] | None = None
    payment_name: str
    is_active: bool

    class Config:
        from_attributes = True


class DeleteCategory(BaseModel):
    category_id: int

    class Config:
        from_attributes = True


class DeletePayment(BaseModel):
    payment_id: int

    class Config:
        from_attributes = True


class GetAllCategories(BaseModel):
    status: int
    data: List[Categories]
    message: str

    class Config:
        from_attributes = True


class GetAllPaymentMethods(BaseModel):
    status: int
    data: List[Payment]
    message: str

    class Config:
        from_attributes = True


class UpdateStock(BaseModel):
    stock_id: int
    stock: int
    variant_id: int
    increment: bool

    class Config:
        from_attributes = True


class ItemsOrdered(BaseModel):
    variant_id: int
    count: int


class BookOrder(Modifier):
    items_ordered: List
    customer_contact: int
    payment_status: str
    payment_type: str
    customer_name: str | None = None
    discount_total: float | None = None
    total_amount: float
    subtotal: float


class AddEmployee(Modifier):
    employee_id: str = ""
    company_id: Optional[str] | None = None
    employee_name: str
    employee_contact: int
    employee_email: str
    employee_gender: str
    employee_image: str
    DOJ: date
    DOB: date
    employee_address: str
    aadhar_no: int
    pan_no: int
    employee_ifsc_code: str
    employee_acc_no: int
    employee_bank_name: str
    employee_upi_code:str
    employee_salary: float
    active_status: ActivityStatus = "ACTIVE"

    class Config:
        from_attributes = True


class Modules(BaseModel):
    module_id: Optional[int] | None = None
    module_name: str
    base_cost: int

    class Config:
        from_attributes = True


class Roles(BaseModel):
    role_id: Optional[int] | None = None
    role_name: str

    class Config:
        from_attributes = True


class AuthBranches(Branch):
    modules: List[Modules]
    role: List[Roles]

    class Config:
        from_attributes = True


class AuthenticationResponse(Companies):
    branches: List[AuthBranches]


class AddCustomer(BaseModel):
    customer_name: str
    customer_number: str
    customer_address: str
    customer_birthdate: date
    customer_points: int
    customer_status: ActivityStatus = "ACTIVE"
    company_id: Optional[str] | None = None


class UpdateCustomer(AddCustomer):
    modified_by: Optional[str] | None = None
    modified_on: date = datetime.now()

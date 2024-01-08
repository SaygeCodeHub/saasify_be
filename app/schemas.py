from __future__ import annotations

from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import date


class Companies(BaseModel):
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

    class Config:
        from_attributes = True


class Branch(BaseModel):
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


class Categories(BaseModel):
    category_id: Optional[int] | None = None
    category_name: str
    is_active: bool

    class Config:
        from_attributes = True


class Payment(BaseModel):
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


class BookOrder(BaseModel):
    items_ordered: List
    customer_contact: int
    payment_status: str
    payment_type: str
    customer_name: str | None = None
    discount_total: float | None = None
    total_amount: float
    subtotal: float


class AddEmployee(BaseModel):
    employee_id: Optional[int] | None = None
    company_id: int
    branch_id: int
    employee_name: str
    employee_contact: int
    email: str
    employee_gender: str
    DOJ: date
    DOB: date
    type: str
    role: List[int]

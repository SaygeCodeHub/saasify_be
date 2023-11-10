from typing import Optional, List
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


class GetBranch(BaseModel):
    data: Branch

    class Config:
        from_attributes = True


class AddVariants(BaseModel):
    product_id: int
    stock: int
    barcode: int
    cost: float
    quantity: int
    unit: str
    images: List[str]
    draft: bool
    restock_reminder: int
    discount_percent: Optional[float] | None = None

    class Config:
        from_attributes = True


class AddProducts(BaseModel):
    product_id: Optional[int] | None = None
    category_name: str
    brand_name: str
    stock: int | None = 0
    product_name: str
    barcode: int
    product_description: str
    cost: float
    quantity: int
    unit: str
    images: List[str]
    draft: bool
    restock_reminder: int
    discount_percent: Optional[float] | None = None

    class Config:
        from_attributes = True


class EditProduct(AddProducts):
    variant_id: Optional[int] | None = None

    class Config:
        from_attributes = True


class DeleteVariants(BaseModel):
    variant_ids: List[int]

    class Config:
        from_attributes = True


class Categories(BaseModel):
    category_id: int
    category_name: str

    class Config:
        from_attributes = True


class GetAllCategories(BaseModel):
    status: int
    data: List[Categories]
    message: str

    class Config:
        from_attributes = True

"""Schemas for Model - Products"""
from typing import List

from pydantic import BaseModel

from app.v2_0.HRMS.domain.schemas.modifier_schemas import Modifier
from app.v2_0.POS.domain.schemas.variant_schemas import InitVariant, GetVariants


class UpdateProduct(Modifier):
    product_name: str
    description: str
    image: str


class AddProduct(UpdateProduct, InitVariant):
    category_id: int

    variant_name: str = ""
    company_id: int = None
    branch_id: int = None


class GetProducts(BaseModel):
    product_name: str
    description: str
    product_id: int
    product_image: str
    variants: List[GetVariants]

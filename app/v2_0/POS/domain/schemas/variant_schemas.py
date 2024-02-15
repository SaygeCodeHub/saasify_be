"""Schemas for Model - ProductVariants"""
from pydantic import BaseModel

from app.v2_0.HRMS.domain.schemas.modifier_schemas import Modifier
from app.v2_0.enums import Unit


class InitVariant(BaseModel):
    unit: Unit
    quantity: str
    price: float


class UpdateVariant(Modifier):
    variant_name: str = ""
    quantity: str
    price: float
    unit: Unit


class AddVariant(UpdateVariant):
    unit: Unit
    product_id: int
    category_id: int
    company_id: int = None
    branch_id: int = None


class GetVariants(BaseModel):
    variant_id: int
    variant_name: str
    quantity: str
    unit: str
    price: float

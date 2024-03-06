"""Schemas for Model - ProductVariants"""
from pydantic import BaseModel

from app.enums.unit_enum import Unit
from app.v3_0.schemas.modifier_schemas import Modifier


class InitVariant(BaseModel):
    unit: Unit
    measuring_qty: str
    stock_qty: int
    price: float


class UpdateVariant(Modifier):
    variant_name: str = ""
    measuring_qty: str
    stock_qty: int
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
    measuring_qty: str
    unit: str
    price: float

"""Schemas for Inventory"""
from pydantic import BaseModel


class GetAllInventory(BaseModel):
    variant_name: str
    measuring_qty: str
    stock_qty: int
    unit: str
    price: float
    product_id: int

"""Schemas for model - Orders"""
from typing import Dict, List

from pydantic import BaseModel
from app.v2_0.enums import TaskStatus


class PlaceOrder(BaseModel):
    customer_name: str
    customer_contact: int
    placed_by: int = None
    products_ordered: List[Dict]
    grand_total: float
    payment_type: str = ""
    payment_status: TaskStatus
    gst: float = None
    discount_amount: float = None

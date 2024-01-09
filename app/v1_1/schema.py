from pydantic import BaseModel
from datetime import date

from app.v1_1.models import CustomerStatus


class AddCustomer(BaseModel):
    customer_name: str
    customer_number: str
    customer_address: str
    customer_birthdate: date
    customer_points: int
    customer_status: CustomerStatus

from typing import Optional

from pydantic import BaseModel
from datetime import date, datetime

from app.v1_1.models import CustomerStatus


class AddCustomer(BaseModel):
    customer_name: str
    customer_number: str
    customer_address: str
    customer_birthdate: date
    customer_points: int
    customer_status: CustomerStatus = "ACTIVE"
    company_id: Optional[str] | None = None


class UpdateCustomer(AddCustomer):
    modified_by: Optional[str] | None = None
    modified_on: date = datetime.now()

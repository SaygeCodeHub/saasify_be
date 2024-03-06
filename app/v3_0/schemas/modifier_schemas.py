"""Schemas for different models are written here"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Modifier(BaseModel):
    """Contains all the fields that will be inherited by other schemas """
    modified_on: Optional[datetime] = None
    modified_by: Optional[int] = None

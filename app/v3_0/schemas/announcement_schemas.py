"""Schemas for model - Announcements"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.v3_0.schemas.modifier_schemas import Modifier


class AddAnnouncement(BaseModel):
    due_date: date
    description: str
    company_id: int = None


class GetAnnouncements(BaseModel):
    id: int
    due_date: date
    description: str
    is_active: bool
    published_time: Optional[datetime] = datetime.now()


class UpdateAnnouncement(Modifier):
    id: int
    due_date: date
    description: str
    is_active: bool

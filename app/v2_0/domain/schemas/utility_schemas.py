"""Schemas for providing utility"""
from typing import Optional, List

from pydantic import BaseModel

from app.v2_0.domain.models.enums import DesignationEnum, Modules


class Credentials(BaseModel):
    """Used to get the credentials of an individual"""
    email: str
    token: Optional[str] = None
    password: str


class JsonObject(BaseModel):
    """Used to get selected json fields from FE"""
    email: Optional[str] = None


class UserDataResponse(BaseModel):
    branch_id: int
    branch_name: str
    designations: List[DesignationEnum]
    accessible_modules: List[Modules]
    # accessible_features: List[Features]

"""Schemas for providing utility"""
from typing import Optional, List

from pydantic import BaseModel

from app.v2_0.domain.models.enums import DesignationEnum, Modules, Features


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
    accessible_features: List[Features]


class GetUserDataResponse(BaseModel):
    company_id: int
    company_name: str
    branches: List


class FirebasePushNotificationJson(BaseModel):
    device_token: str
    title: str
    body: str

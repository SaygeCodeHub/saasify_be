"""Schemas for providing utility"""
from typing import Optional, List

from pydantic import BaseModel

from app.enums.features_enum import Features
from app.enums.modules_enum import Modules


class DeviceToken(BaseModel):
    device_token: str


class Credentials(BaseModel):
    """Used to get the credentials of an individual"""
    email: Optional[str] = None
    token: Optional[str] = None
    password: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.email == "":
            self.email = None
        if self.token == "":
            self.token = None
        if self.password == "":
            self.password = None


class JsonObject(BaseModel):
    """Used to get selected json fields from FE"""
    email: Optional[str] = None


class UserDataResponse(BaseModel):
    branch_id: int
    branch_name: str
    designations: List[str]
    accessible_modules: List[Modules]
    accessible_features: List[Features]


class GetUserDataResponse(BaseModel):
    company_id: int
    company_name: str
    branches: List

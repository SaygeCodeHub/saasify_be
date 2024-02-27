"""Schemas for -  Module"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from app.enums.modules_enum import Modules
from app.v2_0.HRMS.domain.schemas.modifier_schemas import Modifier


class ModuleSchema(Modifier):
    modules: List[Modules]


class ModuleInfoResponse(BaseModel):
    module_name: str


class GetSubscribedModules(BaseModel):
    module_name: str
    is_subscribed: bool
    start_date: date
    end_date: date


class FeaturesMap(BaseModel):
    feature_key: str
    feature_id: float
    is_statistics: bool
    title: str
    icon: str
    value: str
    is_view: bool
    build_screen_endpoint: Optional[str]


class ModulesMap(BaseModel):
    module_key: str
    module_id: int
    title: str
    icon: str
    accessible_features: List[FeaturesMap]


class AvailableModulesMap(BaseModel):
    module_key: str
    module_id: int
    title: str
    icon: str
    available_features: List[FeaturesMap]

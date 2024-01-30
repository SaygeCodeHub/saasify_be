"""Schemas for -  Module"""
from datetime import date
from typing import List

from app.v2_0.domain.models.enums import Modules
from app.v2_0.domain.schemas.modifier_schemas import Modifier


class ModuleSchema(Modifier):
    modules: List[Modules]

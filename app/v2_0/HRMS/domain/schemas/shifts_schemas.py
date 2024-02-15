"""Schemas for the model - Shifts"""
from datetime import time

from pydantic import BaseModel

from app.v2_0.HRMS.domain.schemas.modifier_schemas import Modifier


class BasicShiftParameters(BaseModel):
    shift_name: str
    start_time: time
    end_time: time


class AddShift(BasicShiftParameters):
    company_id: int = None
    branch_id: int = None


class GetShifts(BasicShiftParameters):
    shift_id: int


class UpdateShift(Modifier, BasicShiftParameters):
    pass

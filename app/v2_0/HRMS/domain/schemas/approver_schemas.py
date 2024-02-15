"""Schemas for Approver"""
from typing import List

from pydantic import BaseModel


class AddApprover(BaseModel):
    approvers: List

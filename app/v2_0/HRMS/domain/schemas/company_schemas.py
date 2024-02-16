"""Schemas for Company"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.v2_0.enums import ActivityStatus
from app.v2_0.HRMS.domain.schemas.branch_schemas import AddBranch, CreateBranchResponse
from app.v2_0.HRMS.domain.schemas.modifier_schemas import Modifier


class UpdateCompany(Modifier):
    company_name: Optional[str] | None = None
    company_domain: str = None
    company_logo: str = None
    company_email: str = None
    services: str = None
    owner: int = None
    activity_status: ActivityStatus = ActivityStatus.ACTIVE


class AddCompany(AddBranch, UpdateCompany):
    """Contains all the fields that will be accessible to all objects of type - 'Company' """
    onboarding_date: date = datetime.now()


class GetCompany(BaseModel):
    company_id: int
    company_name: Optional[str]
    owner: Optional[int]
    activity_status: Optional[ActivityStatus]


class AddCompanyResponse(BaseModel):
    company_name: str
    company_id: int
    branch: CreateBranchResponse

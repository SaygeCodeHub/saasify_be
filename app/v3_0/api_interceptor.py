"""This file contains all the APIs that will be called for plotting forms and tables"""
from typing import Optional

from fastapi import APIRouter, Depends

from app.infrastructure.database import get_db
from app.v3_0.schemas.form_schema import DynamicForm
from app.v3_0.service.build_service import plot_announcement_form, add_dynamic_announcements, \
    change_dynamic_announcement_data

router = APIRouter()


@router.get("/v3.0/buildAnnouncementForm")
def build_announcement_form():
    return plot_announcement_form()


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/addAnnouncements")
def create_announcements(announcement: DynamicForm, user_id: int, company_id: int, branch_id: int,
                         db=Depends(get_db)):
    return add_dynamic_announcements(announcement, user_id, company_id, branch_id, db)


@router.put("/v3.0/{company_id}/{branch_id}/{user_id}/updateAnnouncements")
def update_announcements(announcement: DynamicForm, user_id: int, company_id: int, branch_id: int,
                         announcement_id: Optional[str] = None,
                         db=Depends(get_db)):
    return change_dynamic_announcement_data(announcement, user_id, company_id, branch_id, announcement_id, db)

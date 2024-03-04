"""This file contains all the APIs that will be called for plotting forms and tables"""
from typing import Optional

from fastapi import APIRouter, Depends

from app.infrastructure.database import get_db
from app.v2_0.HRMS.domain.schemas.utility_schemas import DeviceToken
from app.v3_0.schemas.form_schema import DynamicForm
from app.v3_0.service.build_service import plot_announcement_form, add_dynamic_announcements, \
    change_dynamic_announcement_data, fetch_by_id
from app.v3_0.service.home_screen_service import fetch_home_screen_data
from app.v3_0.service.tasks_services import plot_tasks_form, add_dynamic_tasks

router = APIRouter()


@router.get("/v3.0/buildAnnouncementForm")
def build_announcement_form():
    return plot_announcement_form()


@router.get("/v3.0/{company_id}/{branch_id}/{user_id}/getUser/{u_id}")
def get_user_by_id(u_id: int, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    """u_id is the id of the person being fetched"""
    return fetch_by_id(u_id, user_id, company_id, branch_id, db)


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/addAnnouncements")
def create_announcements(announcement: DynamicForm, user_id: int, company_id: int, branch_id: int,
                         db=Depends(get_db)):
    return add_dynamic_announcements(announcement, user_id, company_id, branch_id, db)


@router.put("/v3.0/{company_id}/{branch_id}/{user_id}/updateAnnouncements")
def update_announcements(announcement: DynamicForm, user_id: int, company_id: int, branch_id: int,
                         announcement_id: Optional[str] = None,
                         db=Depends(get_db)):
    return change_dynamic_announcement_data(announcement, user_id, company_id, branch_id, announcement_id, db)


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/initializeApi")
def get_home_screen_data(device_token_obj: DeviceToken, user_id: int, company_id: int, branch_id: int,
                         db=Depends(get_db)):
    return fetch_home_screen_data(device_token_obj, user_id, company_id, branch_id, db)


@router.get("/v3.0/{company_id}/{branch_id}/{user_id}/buildTaskForm")
def build_announcement_form(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return plot_tasks_form(branch_id, db)


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/addTasks")
def create_tasks(tasks: DynamicForm, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return add_dynamic_tasks(tasks, company_id, branch_id, user_id, db)

"""This file contains all the APIs that will be called for plotting forms and tables"""
from typing import Optional

from fastapi import APIRouter, Depends

from app.infrastructure.database import get_db
from app.v3_0.schemas.form_schema import DynamicForm
from app.v3_0.schemas.screen_schema import BuildScreen
from app.v3_0.schemas.utility_schemas import DeviceToken
from app.v3_0.service.build_service import add_dynamic_announcements, \
    change_dynamic_announcement_data, fetch_by_id
from app.v3_0.service.category_service import add_category
from app.v3_0.service.employees_schema import build_add_employee_form
from app.v3_0.service.form_plotting_service import plot_announcement_form, plot_category_form
from app.v3_0.service.home_screen_service import fetch_home_screen_data
from app.v3_0.service.leaves_srevice import build_apply_leave_form, add_dynamic_leaves, fetch_my_leaves, \
    fetch_pending_leaves
from app.v3_0.service.tasks_services import plot_tasks_form, add_dynamic_tasks

router = APIRouter()

"""----------------------------------------------Form building  APIs-------------------------------------------------------------------"""


@router.get("/v3.0/{company_id}/{branch_id}/{user_id}/buildAnnouncementForm")
def build_announcement_form(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return plot_announcement_form(db)


@router.get("/v3.0/buildCategoryForm")
def build_category_form():
    return plot_category_form()


"""----------------------------------------------Category related APIs-------------------------------------------------------------------"""


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/addCategory")
def create_category(category: DynamicForm, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return add_category(category, company_id, branch_id, user_id, db)


# @router.put("/v3.0/{company_id}/{branch_id}/{user_id}/updateCategory/{cat_id}")
# def update_category(category: DynamicForm, cat_id: int, company_id: int, branch_id: int, user_id: int,
#                     db=Depends(get_db)):
#     return modify_category(category, cat_id, company_id, branch_id, user_id, db)


"""----------------------------------------------User related APIs-------------------------------------------------------------------"""


@router.get("/v3.0/{company_id}/{branch_id}/{user_id}/getUser/{u_id}")
def get_user_by_id(u_id: int, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    """u_id is the id of the person being fetched"""
    return fetch_by_id(u_id, user_id, company_id, branch_id, db)


"""----------------------------------------------Announcements related APIs-------------------------------------------------------------------"""


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/addAnnouncement")
def create_announcements(announcement: DynamicForm, user_id: int, company_id: int, branch_id: int,
                         db=Depends(get_db)):
    return add_dynamic_announcements(announcement, user_id, company_id, branch_id, db)


@router.put("/v3.0/{company_id}/{branch_id}/{user_id}/updateAnnouncements")
def update_announcements(announcement: DynamicForm, user_id: int, company_id: int, branch_id: int,
                         announcement_id: Optional[str] = None,
                         db=Depends(get_db)):
    return change_dynamic_announcement_data(announcement, user_id, company_id, branch_id, announcement_id, db)


"""----------------------------------------------Home Screen API-------------------------------------------------------------------"""


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/initializeApi")
def get_home_screen_data(device_token_obj: DeviceToken, user_id: int, company_id: int, branch_id: int,
                         db=Depends(get_db)):
    return fetch_home_screen_data(device_token_obj, user_id, company_id, branch_id, db)


"""----------------------------------------------Task API-------------------------------------------------------------------"""


@router.get("/v3.0/{company_id}/{branch_id}/{user_id}/buildTaskForm")
def build_task_form(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return plot_tasks_form(branch_id, db)


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/addTasks")
def create_tasks(tasks: DynamicForm, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return add_dynamic_tasks(tasks, company_id, branch_id, user_id, db)


"""----------------------------------------------Leaves API-------------------------------------------------------------------"""


@router.get("/v3.0/{company_id}/{branch_id}/{user_id}/buildApplyLeaveForm")
def build_leave_form(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return build_apply_leave_form(company_id, branch_id, user_id, db)


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/addLeave")
async def create_dynamic_leaves(new_leave: DynamicForm, user_id: int, company_id: int, branch_id: int,
                                db=Depends(get_db)):
    return await add_dynamic_leaves(new_leave, company_id, branch_id, user_id, db)


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/getMyLeaves")
def get_my_leaves(buildScreen: BuildScreen, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    """Fetches all the leaves applied by a user. Additionally, if the user is also an approver, pending leaves will be fetched too"""
    return fetch_my_leaves(buildScreen, company_id, branch_id, user_id, db)


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/getPendingLeaves")
def get_pending_leaves(buildScreen: BuildScreen, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    """Fetches all the leaves applied by a user. Additionally, if the user is also an approver, pending leaves will be fetched too"""
    return fetch_pending_leaves(buildScreen, company_id, branch_id, user_id, db)


@router.put("/v3.0/{company_id}/{branch_id}/{user_id}/buildUpdateLeaveStatus/{u_id}")
def build_update_leave_status(u_id: int, status: str, company_id: int, branch_id: int, user_id: int,
                              db=Depends(get_db)):
    """Updates the status of a leave"""
    return


"""----------------------------------------------Employee API-------------------------------------------------------------------"""


@router.get("/v3.0/{company_id}/{branch_id}/{user_id}/buildEmployeeForm")
def build_employee_form(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return build_add_employee_form(company_id, branch_id, user_id, db)

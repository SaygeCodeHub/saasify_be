"""Apis are intercepted in this file"""
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends

from app.v2_0.HRMS.application.password_handler.pwd_encrypter_decrypter import verify
from app.v2_0.HRMS.application.password_handler.reset_password import initiate_pwd_reset, change_password, check_token
from app.v2_0.HRMS.application.service.announcement_service import add_announcements, fetch_announcements, \
    change_announcement_data, remove_announcement
from app.v2_0.HRMS.application.service.attendance_service import mark_attendance_func, get_todays_attendance, \
    attendance_history_func
from app.v2_0.HRMS.application.service.company_service import add_company, fetch_company, modify_company, \
    modify_branch, fetch_branches, get_all_user_data, modify_branch_settings, fetch_branch_settings, add_new_branch
from app.v2_0.HRMS.application.service.employee_service import invite_employee, fetch_employees, fetch_employee_salaries
from app.v2_0.HRMS.application.service.home_screen_service import fetch_home_screen_data
from app.v2_0.HRMS.application.service.leave_service import get_screen_apply_leave, apply_for_leave, fetch_leaves, \
    fetch_all_leaves, modify_leave_status, withdraw_leave_func
from app.v2_0.HRMS.application.service.module_service import add_module, fetch_subscribed_modules, fetch_all_modules
from app.v2_0.HRMS.application.service.shift_service import add_shift, fetch_all_shifts, change_shift_info, \
    remove_shift, \
    assign_shift_to_employee
from app.v2_0.HRMS.application.service.task_service import assign_task, fetch_my_tasks, change_task_status
from app.v2_0.HRMS.application.service.update_user_service import user_update_func
from app.v2_0.HRMS.application.service.user_service import add_user, fetch_by_id, update_approver
from app.v2_0.HRMS.domain.models.user_auth import UsersAuth
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.schemas.announcement_schemas import AddAnnouncement, UpdateAnnouncement
from app.v2_0.HRMS.domain.schemas.approver_schemas import AddApprover
from app.v2_0.HRMS.domain.schemas.branch_schemas import AddBranch, UpdateBranch
from app.v2_0.HRMS.domain.schemas.branch_settings_schemas import UpdateBranchSettings
from app.v2_0.HRMS.domain.schemas.company_schemas import AddCompany, UpdateCompany
from app.v2_0.HRMS.domain.schemas.employee_schemas import InviteEmployee
from app.v2_0.HRMS.domain.schemas.leaves_schemas import ApplyLeave, UpdateLeave
from app.v2_0.HRMS.domain.schemas.module_schemas import ModuleSchema
from app.v2_0.HRMS.domain.schemas.shifts_schemas import AddShift, UpdateShift
from app.v2_0.HRMS.domain.schemas.task_schemas import AssignTask, UpdateTask
from app.v2_0.HRMS.domain.schemas.user_schemas import AddUser, UpdateUser, LoginResponse
from app.v2_0.HRMS.domain.schemas.utility_schemas import Credentials, JsonObject, DeviceToken
from app.v2_0.dto.dto_classes import ResponseDTO
from app.v2_0.infrastructure.database import engine, get_db, Base

router = APIRouter()
Base.metadata.create_all(bind=engine)

"""----------------------------------------------User related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/registerUser")
def register_user(user: AddUser, db=Depends(get_db)):
    """Calls service layer to create a new user"""
    return add_user(user, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getUser/{u_id}")
def get_user_by_id(u_id: int, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    """u_id is the id of the person being fetched"""
    return fetch_by_id(u_id, user_id, company_id, branch_id, db)


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/updateUser")
def update_user(user: UpdateUser, user_id: int, company_id: int, branch_id: int, u_id: Optional[str] = None,
                db=Depends(get_db)):
    """Calls service layer to update user"""
    return user_update_func(user, user_id, company_id, branch_id, u_id, db)


@router.post("/v2.0/authenticateUser")
def login(credentials: Credentials, db=Depends(get_db)):
    """User Login"""
    try:
        email = credentials.email
        pwd = credentials.password

        is_user_present = db.query(UsersAuth).filter(UsersAuth.user_email == email).first()

        if is_user_present is None:
            return ResponseDTO(404, "User is not registered, please register.", {})

        if is_user_present.password is None:
            return ResponseDTO(404, "Password is not set yet. Please set your password", {})

        if not verify(pwd, is_user_present.password):
            return ResponseDTO(401, "Password Incorrect!", {})

        # Get all user data
        user_details = db.query(UserDetails).filter(
            UserDetails.user_id == is_user_present.user_id).first()

        ucb = db.query(UserCompanyBranch).filter(
            UserCompanyBranch.user_id == is_user_present.user_id).first()
        if ucb.company_id:
            complete_data = get_all_user_data(ucb, db)
            data = [complete_data]
        else:
            data = []

        return ResponseDTO(200, "Login successful",
                           LoginResponse(user_id=is_user_present.user_id,
                                         name=user_details.first_name + " " + user_details.last_name, company=data))

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


@router.post("/v2.0/forgotPassword")
def forgot_password(email: JsonObject, db=Depends(get_db)):
    """Calls the service layer to send an email for password reset"""
    return initiate_pwd_reset(email.model_dump()["email"], db)


@router.post("/v2.0/sendVerificationLink")
def verify_token(obj: Credentials, db=Depends(get_db)):
    """Calls the service layer to verify the token received by an individual"""
    return check_token(obj, db)


@router.put("/v2.0/updatePassword")
def update_password(obj: Credentials, db=Depends(get_db)):
    """Calls the service layer to update the password of an individual"""
    return change_password(obj, db)


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/sendInvite")
def send_employee_invite(employee: InviteEmployee, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return invite_employee(employee, user_id, company_id, branch_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getEmployees")
def get_employees(branch_id: int, company_id: int, user_id: str, db=Depends(get_db)):
    return fetch_employees(company_id, branch_id, user_id, db)


"""----------------------------------------------Company related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{user_id}/createCompany")
def create_company(company: AddCompany, user_id: int, db=Depends(get_db)):
    return add_company(company, user_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getCompany")
def get_company(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return fetch_company(user_id, company_id, branch_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateCompany/{comp_id}")
def update_company(company: UpdateCompany, user_id: int, company_id: int, branch_id: int, comp_id: int,
                   db=Depends(get_db)):
    return modify_company(company, user_id, company_id, branch_id, comp_id, db)


"""----------------------------------------------Branch related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/createBranch")
def create_branch(branch: AddBranch, user_id: int, branch_id: int, company_id: int, db=Depends(get_db)):
    return add_new_branch(branch, user_id, branch_id, company_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateBranch")
def update_branch(branch: UpdateBranch, user_id: int, branch_id: int, company_id: int, bran_id: int,
                  db=Depends(get_db)):
    return modify_branch(branch, user_id, company_id, branch_id, bran_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getBranches")
def get_branches(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return fetch_branches(user_id, company_id, branch_id, db)


"""----------------------------------------------Branch Settings related APIs-------------------------------------------------------------------"""


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateBranchSettings")
def update_branch_settings(settings: UpdateBranchSettings, user_id: int, company_id: int, branch_id: int,
                           db=Depends(get_db)):
    return modify_branch_settings(settings, user_id, company_id, branch_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getBranchSettings")
def get_branch_settings(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return fetch_branch_settings(user_id, company_id, branch_id, db)


"""----------------------------------------------Leave related APIs-------------------------------------------------------------------"""


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/loadApplyLeaveScreen")
def load_apply_leave_screen(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return get_screen_apply_leave(user_id, company_id, branch_id, db)


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/applyLeave")
def apply_leave(leave_application: ApplyLeave, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return apply_for_leave(leave_application, user_id, company_id, branch_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/myLeaves")
def get_leaves(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return fetch_leaves(user_id, company_id, branch_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getAllLeaves")
def get_all_leaves(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return fetch_all_leaves(user_id, company_id, branch_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateLeaveStatus")
def update_leave_status(application_response: UpdateLeave, user_id: int, company_id: int, branch_id: int,
                        db=Depends(get_db)):
    return modify_leave_status(application_response, user_id, company_id, branch_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/withdrawLeave")
def update_leave_status(leave_id: int, user_id: int, company_id: int, branch_id: int,
                        db=Depends(get_db)):
    return withdraw_leave_func(leave_id, user_id, company_id, branch_id, db)


"""----------------------------------------------Approver related APIs-------------------------------------------------------------------"""


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateApprover")
def add_approver(approver: AddApprover, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return update_approver(approver, user_id, company_id, branch_id, db)


"""----------------------------------------------Attendance related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/markAttendance")
def mark_attendance(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return mark_attendance_func(company_id, branch_id, user_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/todayAttendance")
def today_attendance(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return get_todays_attendance(user_id, company_id, branch_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/attendanceHistory")
def attendance_history(user_id: int, company_id: int, branch_id: int, db=Depends(get_db), u_id: Optional[str] = None):
    return attendance_history_func(user_id, company_id, branch_id, db, u_id)


"""----------------------------------------------Module related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/addModules")
def subscribe_module(module: ModuleSchema, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return add_module(module, user_id, branch_id, company_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getSubscribedModules")
def get_subscribed_modules(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return fetch_subscribed_modules(user_id, company_id, branch_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getAllModules")
def get_all_modules(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return fetch_all_modules(user_id, company_id, branch_id, db)


"""----------------------------------------------Payroll related APIs-------------------------------------------------------------------"""


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getSalaries")
def get_employee_salaries(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return fetch_employee_salaries(user_id, company_id, branch_id, db)


"""----------------------------------------------Home Screen API-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/initializeApi")
def get_home_screen_data(device_token_obj: DeviceToken, user_id: int, company_id: int, branch_id: int,
                         db=Depends(get_db)):
    return fetch_home_screen_data(device_token_obj, user_id, company_id, branch_id, db)


"""----------------------------------------------Task related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/assignTask")
def create_task(assigned_task: AssignTask, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return assign_task(assigned_task, user_id, company_id, branch_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getTasks")
def get_my_tasks(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return fetch_my_tasks(user_id, company_id, branch_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateTaskStatus")
def update_task(updated_task: UpdateTask, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return change_task_status(updated_task, user_id, company_id, branch_id, db)


"""----------------------------------------------Announcement related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/addAnnouncements")
def create_announcements(announcement: AddAnnouncement, user_id: int, company_id: int, branch_id: int,
                         db=Depends(get_db)):
    return add_announcements(announcement, user_id, company_id, branch_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getAnnouncements")
def get_all_announcements(user_id: int, company_id: int, branch_id: int,
                          db=Depends(get_db)):
    return fetch_announcements(user_id, company_id, branch_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateAnnouncements")
def update_announcements(announcement: UpdateAnnouncement, user_id: int, company_id: int, branch_id: int,
                         db=Depends(get_db)):
    return change_announcement_data(announcement, user_id, company_id, branch_id, db)


@router.delete("/v2.0/{company_id}/{branch_id}/{user_id}/deleteAnnouncements/{announcement_id}")
def delete_announcement(announcement_id: int, user_id: int, company_id: int, branch_id: int,
                        db=Depends(get_db)):
    return remove_announcement(announcement_id, user_id, company_id, branch_id, db)


"""----------------------------------------------Shift related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/createShift")
def create_shift(shift: AddShift, user_id: int, company_id: int, branch_id: int,
                 db=Depends(get_db)):
    return add_shift(shift, user_id, company_id, branch_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getAllShifts")
def get_all_shifts(user_id: int, company_id: int, branch_id: int,
                   db=Depends(get_db)):
    return fetch_all_shifts(user_id, company_id, branch_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateShift/{shift_id}")
def update_shift(new_shift_info: UpdateShift, user_id: int, company_id: int, branch_id: int, shift_id: int,
                 db=Depends(get_db)):
    return change_shift_info(new_shift_info, user_id, company_id, branch_id, shift_id, db)


@router.delete("/v2.0/{company_id}/{branch_id}/{user_id}/deleteShift/{shift_id}")
def delete_shift(user_id: int, company_id: int, branch_id: int, shift_id: int,
                 db=Depends(get_db)):
    return remove_shift(user_id, company_id, branch_id, shift_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/assignShift/{u_id}/{shift_id}")
def assign_shift(user_id: int, company_id: int, branch_id: int, u_id: int, shift_id: int,
                 db=Depends(get_db)):
    return assign_shift_to_employee(user_id, company_id, branch_id, u_id, shift_id, db)

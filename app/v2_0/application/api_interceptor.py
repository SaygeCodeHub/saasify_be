"""Apis are intercepted in this file"""
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from fastapi import Depends

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.password_handler.pwd_encrypter_decrypter import verify
from app.v2_0.application.password_handler.reset_password import initiate_pwd_reset, check_token, change_password
from app.v2_0.application.service.attendance_service import mark_attendance_func, get_todays_attendance, \
    attendance_history_func
from app.v2_0.application.service.company_service import add_company, add_branch, fetch_company, modify_company, \
    modify_branch, fetch_branches, get_all_user_data, modify_branch_settings, fetch_branch_settings
from app.v2_0.application.service.employee_service import invite_employee, fetch_employees
from app.v2_0.application.service.leave_service import get_screen_apply_leave, apply_for_leave, fetch_leaves, \
    fetch_pending_leaves, modify_leave_status
from app.v2_0.application.service.user_service import add_user, modify_user, fetch_by_id, update_approver
from app.v2_0.domain import models
from app.v2_0.domain.schema import AddUser, PwdResetToken, JSONObject, Credentials, AddCompany, AddBranch, \
    UpdateUser, UpdateCompany, UpdateBranch, UpdateBranchSettings, \
    InviteEmployee, ApplyLeave, UpdateLeave, AddApprover, \
    LoginResponse
from app.v2_0.infrastructure.database import engine, get_db

router = APIRouter()
models.Base.metadata.create_all(bind=engine)

"""----------------------------------------------User related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/registerUser")
def register_user(user: AddUser, db=Depends(get_db)):
    """Calls service layer to create a new user"""
    return add_user(user, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getUser/{u_id}")
def get_user_by_id(u_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    """u_id is the id of the person being fetched"""
    return fetch_by_id(u_id, company_id, branch_id, db)


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/updateUser")
def update_user(user: UpdateUser, user_id: int, company_id: int, branch_id: int, u_id: Optional[str] = None,
                db=Depends(get_db)):
    """Calls service layer to update user"""
    return modify_user(user, user_id, company_id, branch_id, u_id, db)


@router.post("/v2.0/authenticateUser")
def login(credentials: Credentials, db=Depends(get_db)):
    """User Login"""
    try:
        email = credentials.model_dump()["email"]
        pwd = credentials.model_dump()["password"]

        is_user_present = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == email).first()

        if is_user_present is None:
            return ResponseDTO(404, "User is not registered, please register.", {})

        if is_user_present.password is None:
            return ResponseDTO(404, "Password not set yet. Please set your password", {})

        if not verify(pwd, is_user_present.password):
            return ResponseDTO(401, "Password Incorrect!", {})

        # Get all user data
        user_details = db.query(models.UserDetails).filter(
            models.UserDetails.user_id == is_user_present.user_id).first()

        ucb = db.query(models.UserCompanyBranch).filter(
            models.UserCompanyBranch.user_id == is_user_present.user_id).first()
        if ucb.company_id:
            complete_data = get_all_user_data(ucb, db)
            data = [complete_data]
        else:
            data = []

        if user_details.first_name is None and user_details.last_name is None:
            user_details.first_name = ""
            user_details.last_name = ""

        return ResponseDTO(200, "Login successful",
                           LoginResponse(user_id=is_user_present.user_id,
                                         name=user_details.first_name + " " + user_details.last_name, company=data))

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


@router.post("/v2.0/forgotPassword")
def forgot_password(user_email: JSONObject, db=Depends(get_db)):
    """Calls the service layer to send an email for password reset"""
    return initiate_pwd_reset(user_email.model_dump()["email"], db)


@router.post("/v2.0/sendVerificationLink")
def verify_token(token: PwdResetToken, db=Depends(get_db)):
    """Calls the service layer to verify the token received by an individual"""
    return check_token(token.model_dump()["token"], token.model_dump()["email"], token, db)


@router.put("/v2.0/updatePassword")
def update_password(obj: Credentials, db=Depends(get_db)):
    """Calls the service layer to update the password of an individual"""
    return change_password(obj, db)


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/sendInvite")
def send_employee_invite(employee: InviteEmployee, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return invite_employee(employee, user_id, company_id, branch_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getEmployees")
def get_employees(branch_id: int, company_id: int, db=Depends(get_db)):
    return fetch_employees(branch_id, company_id, db)


"""----------------------------------------------Company related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{user_id}/createCompany")
def create_company(company: AddCompany, user_id: int, db=Depends(get_db)):
    return add_company(company, user_id, db)


@router.get("/v2.0/{user_id}/getCompany")
def get_company(user_id: int, db=Depends(get_db)):
    return fetch_company(user_id, db)


@router.put("/v2.0/{company_id}/{user_id}/updateCompany")
def update_company(company: UpdateCompany, user_id: int, company_id: int, db=Depends(get_db)):
    return modify_company(company, user_id, company_id, db)


"""----------------------------------------------Branch related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{user_id}/createBranch")
def create_branch(branch: AddBranch, user_id: int, company_id: int, db=Depends(get_db)):
    return add_branch(branch, user_id, company_id, db, False)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateBranch")
def update_branch(branch: UpdateBranch, user_id: int, branch_id: int, company_id: int, db=Depends(get_db)):
    return modify_branch(branch, user_id, branch_id, company_id, db)


@router.get("/v2.0/{company_id}/{user_id}/getBranches")
def get_branches(user_id: int, company_id: int, db=Depends(get_db)):
    return fetch_branches(user_id, company_id, db)


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


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/pendingLeaveApprovals")
def get_pending_leaves(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return fetch_pending_leaves(user_id, company_id, branch_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateLeaveStatus")
def update_leave_status(application_response: UpdateLeave, user_id: int, company_id: int, branch_id: int,
                        db=Depends(get_db)):
    return modify_leave_status(application_response, user_id, company_id, branch_id, db)


"""----------------------------------------------Approver related APIs-------------------------------------------------------------------"""


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateApprover")
def add_approver(approver: AddApprover, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    return update_approver(approver, user_id, company_id, branch_id, db)


"""----------------------------------------------Push notification APIs-------------------------------------------------------------------"""


@router.post('/v2.0/sendPushNotification')
def send_notification(device_token: str, title: str, body: str):
    server_key = 'AAAAMh0B0ok:APA91bHtNakNYQgnn9uvHfcAMVrQORfb7zLjbeY-VnC6R8e832rld_6OztK2hhMvGQC0gHjvwIr-B5w8t1dTqiE7j7NqGlejQiO7X72Ol-KwzbSN9rWgE8MM3RGlcgDSEjzpmZrXFmKy'
    fcm_endpoint = 'https://fcm.googleapis.com/fcm/send'

    message = {
        'to': device_token,
        'notification': {
            'title': title,
            'body': body,
        },
    }

    headers = {
        'Authorization': f'key={server_key}',
        'Content-Type': 'application/json',
    }

    with httpx.AsyncClient() as client:
        response = client.post(fcm_endpoint, json=message, headers=headers)

        if response.status_code == 200:
            return {'message': 'Notification sent successfully'}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)


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

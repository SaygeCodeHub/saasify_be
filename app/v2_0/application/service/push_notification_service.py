"""Function for firebase push notification"""

import httpx
from fastapi import HTTPException

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.domain.models.leaves import Leaves
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.models.user_details import UserDetails


async def send_notification(device_token: str, title: str, body: str):
    """Communicates with Firebase and sends a notification using FCM"""
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

    async with httpx.AsyncClient() as client:
        response = await client.post(fcm_endpoint, json=message, headers=headers)

        if response.status_code == 200:
            return ResponseDTO(200, "Notification sent successfully", message)
        else:
            return ResponseDTO(204, "Exception!", HTTPException(status_code=response.status_code, detail=response.text))


async def send_leave_notification(leave_application, approvers, applicant_id, company_id, branch_id, db):
    """Sends the leave applied notification to all the approvers"""
    for approver in approvers:
        user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == approver).filter(
            UserCompanyBranch.branch_id == branch_id).filter(UserCompanyBranch.company_id == company_id).first()

        applicant = db.query(UserDetails).filter(UserDetails.user_id == applicant_id).first()
        title = "New leave application!"
        body = f"{applicant.first_name} {applicant.last_name} has applied for a {leave_application.leave_type.name} leave"
        result = await send_notification(user.device_token, title, body)
        print(result.__dict__)


async def send_leave_status_notification(application_response, user_id, company_id, branch_id, db):
    """Send the leave update notification to the applicant"""
    # query = select(UserCompanyBranch.device_token).select_from(UserCompanyBranch).join(Leaves,
    #                                                                                    UserCompanyBranch.user_id == Leaves.user_id).filter(
    #     Leaves.leave_id == application_response.leave_id).filter(Leaves.company_id == company_id).filter(Leaves.branch_id == branch_id)
    # token = db.execute(query)

    leave = db.query(Leaves).filter(Leaves.leave_id == application_response.leave_id).first()
    ucb_entry = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == leave.user_id).filter(
        UserCompanyBranch.branch_id == branch_id).filter(UserCompanyBranch.company_id == company_id).first()
    approver = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    title = f"Leave {application_response.leave_status.name}!"
    body = f"{application_response.comment}. Regards, {approver.first_name} {approver.last_name}. "
    result = await send_notification(ucb_entry.device_token, title, body)
    print(result.__dict__)


async def send_task_assigned_notification(assigned_task, user_id, company_id, branch_id, db):
    """Sends a notification - Task assigned, to the assignee """
    ucb_entry = db.query(UserCompanyBranch).filter(UserCompanyBranch.company_id == company_id).filter(
        UserCompanyBranch.branch_id == branch_id).filter(UserCompanyBranch.user_id == assigned_task.assigned_to).first()
    monitor = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    title = f"New task assigned! - {assigned_task.title}"
    body = f"Description: {assigned_task.task_description}. Priority: {assigned_task.priority.name} Assigned by: {monitor.first_name} {monitor.last_name}"
    result = await send_notification(ucb_entry.device_token, title, body)
    print(result.__dict__)


async def send_task_updated_notification(updated_task, user_id, company_id, branch_id, db):
    """Sends a notification to the assigner telling about the status of task assigned by him"""
    ucb_entry = db.query(UserCompanyBranch).filter(UserCompanyBranch.company_id == company_id).filter(
        UserCompanyBranch.branch_id == branch_id).filter(UserCompanyBranch.user_id == updated_task.monitored_by).first()
    assignee = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    title = f"New task update! - {updated_task.title}"
    body = f"Task assigned to {assignee.first_name} {assignee.last_name} was completed on {updated_task.completion_date}"
    result = await send_notification(ucb_entry.device_token, title, body)
    print(result.__dict__)
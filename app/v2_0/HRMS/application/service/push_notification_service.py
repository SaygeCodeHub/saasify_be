"""Function for firebase push notification"""
from datetime import datetime

import httpx
from fastapi import HTTPException

from app.v2_0.HRMS.domain.models.leaves import Leaves
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.dto.dto_classes import ResponseDTO


async def send_notification(device_token: str, title: str, body: str):
    """Communicates with Firebase and sends a notification using FCM"""
    server_key = 'AAAA4RuOIHM:APA91bGckhCuti3anDnZZUawXAvgCaNndTMk_BBGclPf68VEd93u4SnvfPorOveAYzcJ5kBmHuqbMryag-R6kTqZAUTIG17p_sY7RROhJeqEw2EPUkOfrqBtFbJxW9WacCI1FSz0Jh06'
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
        body = f"{applicant.first_name.title()} {applicant.last_name.title()} has applied for a {leave_application.leave_type.name.title()} leave"
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
    body = f"{application_response.comment}. \n Regards, {approver.first_name.title()} {approver.last_name.title()}. "
    result = await send_notification(ucb_entry.device_token, title, body)
    print(result.__dict__)


async def send_task_assigned_notification(assigned_task, user_id, company_id, branch_id, db):
    """Sends a notification - Task assigned, to the assignee """
    ucb_entry = db.query(UserCompanyBranch).filter(UserCompanyBranch.company_id == company_id).filter(
        UserCompanyBranch.branch_id == branch_id).filter(UserCompanyBranch.user_id == assigned_task.assigned_to).first()
    monitor = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    title = f"New task assigned! - {assigned_task.title}"
    body = f"Description: {assigned_task.task_description}. \n Priority: {assigned_task.priority.name.title()} \n Assigned by: {monitor.first_name} {monitor.last_name}"
    result = await send_notification(ucb_entry.device_token, title, body)
    print(result.__dict__)


async def send_task_updated_notification(updated_task, user_id, company_id, branch_id, db):
    """Sends a notification to the assigner telling about the status of task assigned by him"""
    ucb_entry = db.query(UserCompanyBranch).filter(UserCompanyBranch.company_id == company_id).filter(
        UserCompanyBranch.branch_id == branch_id).filter(UserCompanyBranch.user_id == updated_task.monitored_by).first()
    assignee = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    title = f"New task update! - {updated_task.title}"
    body = f"Task assigned to {assignee.first_name} {assignee.last_name} was completed on {datetime.now().date}"
    closed_body = f"Task assigned to {assignee.first_name} {assignee.last_name} was closed on {datetime.now().date()}"
    result = await send_notification(ucb_entry.device_token, title,
                                     body if updated_task.task_status == "DONE" else closed_body)
    print(result.__dict__)

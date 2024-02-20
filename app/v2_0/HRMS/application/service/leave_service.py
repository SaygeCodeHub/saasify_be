"""Service layer for Leaves"""
import asyncio
from datetime import datetime

from fastapi import Depends
from app.v2_0.dto.dto_classes import ResponseDTO
from app.v2_0.HRMS.application.service.company_service import get_approver_data
from app.v2_0.HRMS.application.service.push_notification_service import send_leave_notification, \
    send_leave_status_notification
from app.v2_0.HRMS.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.companies import Companies
from app.v2_0.enums import LeaveType, LeaveStatus
from app.v2_0.HRMS.domain.models.leaves import Leaves
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.models.user_finance import UserFinance
from app.v2_0.HRMS.domain.schemas.leaves_schemas import LoadApplyLeaveScreen, ApplyLeaveResponse, GetLeaves, \
    GetPendingLeaves, FetchAllLeavesResponse
from app.v2_0.infrastructure.database import get_db


def get_screen_apply_leave(user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            user = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
            ucb_user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()

            approver_data = []

            for a in ucb_user.approvers:
                data = get_approver_data(a, db)
                approver_data.append(data)

            result = LoadApplyLeaveScreen(casual_leaves=user.casual_leaves, medical_leaves=user.medical_leaves,
                                          approvers=approver_data)
            return ResponseDTO(200, "Data loaded!", result)
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def check_remaining_leaves(user_id, leave_application, db):
    user = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    if leave_application.leave_type == LeaveType.CASUAL and user.casual_leaves == 0:
        return 0
    if leave_application.leave_type == LeaveType.MEDICAL and user.medical_leaves == 0:
        return 1
    return 2


def apply_for_leave(leave_application, user_id, company_id, branch_id, db):
    try:
        msg = "Leave application submitted. Change in the number of leaves will be reflected after approval."
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:

            message = check_remaining_leaves(user_id, leave_application, db)

            if message == 0:
                msg = "You have exhausted your casual leaves! Salary will be deducted on approval."
            elif message == 1:
                msg = "You have exhausted your medical leaves! Salary will be deducted on approval."

            leave_application.user_id = user_id
            leave_application.company_id = company_id
            leave_application.branch_id = branch_id
            if len(leave_application.approvers) == 0:
                # company = db.query(Companies).filter(Companies.company_id == company_id).first()
                ucb_approvers = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).filter(
                    UserCompanyBranch.branch_id == branch_id).first()
                leave_application.approvers = ucb_approvers.approvers

            new_leave_application = Leaves(**leave_application.model_dump())
            db.add(new_leave_application)
            db.commit()
            db.refresh(new_leave_application)

            asyncio.run(
                send_leave_notification(leave_application, leave_application.approvers, user_id, company_id, branch_id,
                                        db))

            return ResponseDTO(200, msg,
                               ApplyLeaveResponse(leave_id=new_leave_application.leave_id,
                                                  leave_status=new_leave_application.leave_status.name,
                                                  is_leave_approved=new_leave_application.is_leave_approved,
                                                  comment=new_leave_application.comment))

        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def get_approver_names(approver_ids, db):
    approver_names = []
    for ID in approver_ids:
        approver = db.query(UserDetails).filter(UserDetails.user_id == ID).first()
        approver_names.append(approver.first_name + " " + approver.last_name)
    return approver_names


def fetch_leaves(user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            my_leaves = db.query(Leaves).filter(Leaves.user_id == user_id).all()
            result = [
                GetLeaves(user_id=leave.user_id,
                          leave_type=leave.leave_type.name, leave_id=leave.leave_id, leave_reason=leave.leave_reason,
                          start_date=leave.start_date, end_date=leave.end_date,
                          approvers=get_approver_names(leave.approvers, db),
                          leave_status=leave.leave_status.name, comment=leave.comment)

                for leave in my_leaves
            ]
            if len(my_leaves) == 0:
                return []

            return result
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def get_authorized_leave_requests(pending_leaves, user_id):
    try:
        filtered_leaves = []
        for x in pending_leaves:
            if user_id in x.approvers:
                filtered_leaves.append(x)

        return filtered_leaves
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def format_pending_leaves(filtered_leaves, db):
    for x in filtered_leaves:
        user = db.query(UserDetails).filter(UserDetails.user_id == x.__dict__["user_id"]).first()
        x.__dict__["name"] = user.first_name + " " + user.last_name
    return filtered_leaves


def fetch_all_leaves(user_id, company_id, branch_id, db):
    """Fetches all the leaves applied by a user. Additionally, if the user is also an approver, pending leaves will be fetched too"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:

            # Fetches leaves applied by the user
            my_leaves = fetch_leaves(user_id, company_id, branch_id, db)

            # Fetches the leaves that require approval of the user
            pending_leaves = db.query(Leaves).filter(Leaves.leave_status == LeaveStatus.PENDING).all()
            # Checks if the user is an approver or not
            filtered_leaves = get_authorized_leave_requests(pending_leaves, user_id)

            # If the user is an approver, then show him his leaves and the leaves that require his approval, else, only show his leaves
            leaves_pending = []
            if len(filtered_leaves) != 0:
                final_list = format_pending_leaves(filtered_leaves, db)
                for item in final_list:
                    leaves_pending.append(GetPendingLeaves(leave_id=item.leave_id, user_id=item.user_id, name=item.name,
                                                           leave_type=item.leave_type.name,
                                                           leave_reason=item.leave_reason,
                                                           start_date=item.start_date, end_date=item.end_date,
                                                           approvers=get_approver_names(item.approvers, db)))
                return ResponseDTO(200, "All leaves fetched",
                                   FetchAllLeavesResponse(pending_leaves=leaves_pending, my_leaves=my_leaves))

            if len(my_leaves) == 0:
                return ResponseDTO(200, "You have not applied for any leaves!",
                                   FetchAllLeavesResponse(pending_leaves=[], my_leaves=[]))
            else:
                return ResponseDTO(200, "Leaves fetched!",
                                   FetchAllLeavesResponse(pending_leaves=[], my_leaves=my_leaves))
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def calculate_num_of_leaves(leaveObject, leaves, db):
    """Calculates the number of leaves remaining after approval"""
    duration = (leaveObject.end_date - leaveObject.start_date).days + 1

    for x in range(0, duration):
        leaves = leaves - 1

    if leaves < 0:
        extra_leaves = abs(leaves)
        deduct_salary(leaveObject, extra_leaves, db)
        return 0

    return leaves


def update_user_leaves(leave, db):
    """Updates the number of leaves of an employee"""

    user_query = db.query(UserDetails).filter(UserDetails.user_id == leave.user_id)
    user = user_query.first()

    if leave.leave_type == LeaveType.CASUAL:
        leaves = calculate_num_of_leaves(leave, user.casual_leaves, db)

        user_query.update({"casual_leaves": leaves, "modified_on": datetime.now()})

    else:
        leaves = calculate_num_of_leaves(leave, user.medical_leaves, db)
        user_query.update({"medical_leaves": leaves, "modified_on": datetime.now()})


def deduct_salary(leave, extra_leaves, db):
    """Deducts the salary of an employee for each leave"""
    user_query = db.query(UserFinance).filter(UserFinance.user_id == leave.user_id)
    user = user_query.first()

    if user is None:
        return ResponseDTO(404, "User not found!", {})

    per_day_pay = user.basic_salary / 30 if user.basic_salary is not None else 0 / 30

    calculate_deduction = user.deduction

    for x in range(0, extra_leaves):
        calculate_deduction = calculate_deduction + per_day_pay

    user_query.update({"deduction": calculate_deduction, "modified_on": datetime.now()})


def modify_leave_status(application_response, user_id, company_id, branch_id, db):
    """Leaves are APPROVED or REJECTED using this API"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            leave_query = db.query(Leaves).filter(Leaves.leave_id == application_response.leave_id)
            leave = leave_query.first()
            status = LeaveStatus.REJECTED
            if leave is None:
                return ResponseDTO(404, "Leave entry not found!", {})

            if leave.is_leave_approved is True or leave.leave_status == LeaveStatus.REJECTED:
                return ResponseDTO(200, "Leave already updated!", leave)

            if application_response.is_leave_approved is True:
                status = LeaveStatus.APPROVED
                update_user_leaves(leave, db)

            application_response.leave_status = status
            application_response.modified_by = user_id
            application_response.modified_on = datetime.now()
            leave_query.update(application_response.__dict__)
            db.commit()

            asyncio.run(send_leave_status_notification(application_response, user_id, company_id, branch_id, db))

            return ResponseDTO(200, "Leave status updated!", {})
        else:
            return check

    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def withdraw_leave_func(leave_id: int, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    # try:
    check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

    if check is None:
        leave_query = db.query(Leaves).filter(Leaves.leave_id == leave_id)
        leave = leave_query.first()
        leave_response = {}
        if leave is None:
            return ResponseDTO(204, "Leave entry not found!", {})

        if leave.is_leave_approved is True or leave.leave_status == LeaveStatus.REJECTED or leave.leave_status == LeaveStatus.APPROVED:
            return ResponseDTO(200, "Leave already updated!", leave)

        leave_response["leave_status"] = LeaveStatus.WITHDRAWN
        leave_response["modified_by"] = user_id
        leave_response["modified_on"] = datetime.now()
        leave_response["comment"] = "Leave withdrawn"
        leave_query.update(leave_response)
        db.commit()

        return ResponseDTO(200, "Leave withdrawn successfully", {})
    else:
        return check

# except Exception as exc:
#     db.rollback()
#     return ResponseDTO(204, str(exc), {})

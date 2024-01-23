"""Service layer for Leaves"""
from datetime import datetime

from sqlalchemy import select

from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.domain import models


def get_screen_apply_leave(user_id, company_id, branch_id, db):
    try:
        user = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id).first()
        ucb_user = db.query(models.UserCompanyBranch).filter(models.UserCompanyBranch.user_id == user_id).first()
        return {"casual_leaves": user.casual_leaves, "medical_leaves": user.medical_leaves,
                "approvers": ucb_user.approvers}
    except Exception as exc:
        return ExceptionDTO("get_screen_apply_leave",exc)


def apply_for_leave(leave_application, user_id, company_id, branch_id, db):
    try:
        leave_application.modified_by = user_id
        leave_application.user_id = user_id
        leave_application.company_id = company_id
        leave_application.branch_id = branch_id
        new_leave_application = models.Leaves(**leave_application.model_dump())
        db.add(new_leave_application)
        db.commit()
        db.refresh(new_leave_application)

        return ResponseDTO(200, "Leave application submitted", {})
    except Exception as exc:
        return ExceptionDTO("apply_for_leave",exc)


def fetch_leaves(user_id, company_id, branch_id, db):
    try:
        my_leaves = db.query(models.Leaves).filter(models.Leaves.user_id == user_id).all()

        return my_leaves
    except Exception as exc:
        return ExceptionDTO("fetch_leaves",exc)


def get_authorized_leave_requests(pending_leaves, user_id):
    try:
        filtered_leaves = []
        for x in pending_leaves:
            if user_id in x.__dict__["approvers"]:
                filtered_leaves.append(x)
        return filtered_leaves
    except Exception as exc:
        return ExceptionDTO("get_authorized_leave_requests",exc)


def format_pending_leaves(filtered_leaves, db):
    for x in filtered_leaves:
        user = db.query(models.UserDetails).filter(models.UserDetails.user_id == x.__dict__["user_id"]).first()
        x.__dict__["name"] = user.first_name + " " + user.last_name
    return filtered_leaves


def fetch_pending_leaves(user_id, company_id, branch_id, db):
    try:

        pending_leaves = db.query(models.Leaves).filter(models.Leaves.leave_status == "PENDING").all()
        filtered_leaves = get_authorized_leave_requests(pending_leaves, user_id)

        if len(filtered_leaves) == 0:
            return []
        else:
            final_list = format_pending_leaves(filtered_leaves, db)
        return final_list

    except Exception as exc:
        return ExceptionDTO("fetch_pending_leaves", exc)


def modify_leave_status(application_response, user_id, company_id, branch_id, db):
    try:
        leave_query = db.query(models.Leaves).filter(models.Leaves.leave_id == application_response.leave_id)
        leave = leave_query.first()
        status = "REJECTED"
        if leave is None:
            return ResponseDTO(404, "Leave entry not found!", {})
        if application_response.is_leave_approved is True:
            status = "ACCEPTED"

        application_response.leave_status = status
        application_response.modified_by = user_id
        leave_query.update(application_response.__dict__)
        db.commit()

        return ResponseDTO(200, "Leave status updated!", {})
    except Exception as exc:
        return ExceptionDTO("modify_leave_status", exc)

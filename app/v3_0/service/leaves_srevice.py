from fastapi import Depends, HTTPException

from app.dto.dto_classes import ResponseDTO
from app.infrastructure.database import get_db
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.application.service.company_service import get_approver_data
from app.v2_0.HRMS.application.service.leave_service import check_remaining_leaves
from app.v2_0.HRMS.application.service.push_notification_service import send_leave_notification
from app.v2_0.HRMS.domain.models.leaves import Leaves
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.schemas.leaves_schemas import ApplyLeave
from app.v3_0.forms.add_leaves_form import add_leaves
from app.v3_0.schemas.form_schema import DropdownField, DropdownOption, DynamicForm
from app.v3_0.service.tasks_services import map_to_model


def get_approver_list(user_id, db):
    ucb_user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()

    approver_data = []

    for a in ucb_user.approvers:
        data = get_approver_data(a, db)
        approver_data.append(DropdownOption(label=data.approver_name, value=data.id, option_id=data.id))

    return DropdownField(
        options=approver_data)


def build_apply_leave_form(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    add_leaves.sections[0].fields[0].row_fields[3].dropdown_field = get_approver_list(user_id, db)

    return ResponseDTO(200, "Form plotted!", add_leaves)


async def add_dynamic_leaves(new_leave: DynamicForm, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        msg = "Leave application submitted. Change in the number of leaves will be reflected after approval."
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            approvers=[]
            leaves = db.query(Leaves).filter(Leaves.user_id == user_id).all()
            new_leave = ApplyLeave(
                **map_to_model(new_leave, {"company_id": company_id, "branch_id": branch_id, "user_id": user_id},
                               Leaves()))

            for leave in leaves:
                if (leave.start_date <= new_leave.start_date <= leave.end_date) or (
                        leave.start_date <= new_leave.end_date <= leave.end_date) or (
                        new_leave.start_date < leave.start_date and new_leave.end_date > leave.end_date):
                    return ResponseDTO(204, "You can't apply for a leave on the same dates again!", {})

            message = check_remaining_leaves(user_id, new_leave, db)

            if message == 0:
                msg = "You have exhausted your casual leaves! Salary will be deducted on approval."
            elif message == 1:
                msg = "You have exhausted your medical leaves! Salary will be deducted on approval."

            new_leave.user_id = user_id
            new_leave.company_id = company_id
            new_leave.branch_id = branch_id
            if len(new_leave.approvers) == 0:
                ucb_approvers = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).filter(
                    UserCompanyBranch.branch_id == branch_id).first()
                new_leave.approvers = ucb_approvers.approvers

            new_leave_application = Leaves(**new_leave.model_dump())
            db.add(new_leave_application)
            db.commit()
            db.refresh(new_leave_application)

            await send_leave_notification(new_leave, new_leave.approvers, user_id, company_id,
                                          branch_id, db)
            return ResponseDTO(200, msg, {})

        else:
            return check
    except HTTPException as e:
        return ResponseDTO(204, str(e), {})
    except ValueError as e:
        return ResponseDTO(204, str(e), {})
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

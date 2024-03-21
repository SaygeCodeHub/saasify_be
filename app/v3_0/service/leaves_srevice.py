from fastapi import Depends, HTTPException

from app.dto.dto_classes import ResponseDTO
from app.enums.button_action_enum import ButtonActionEnum
from app.enums.leave_status_enum import LeaveStatus
from app.enums.screen_enums import DataTypeEnum
from app.infrastructure.database import get_db
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.application.service.company_service import get_approver_data
from app.v2_0.HRMS.application.service.leave_service import check_remaining_leaves, get_approver_names, \
    get_authorized_leave_requests, format_pending_leaves
from app.v2_0.HRMS.application.service.push_notification_service import send_leave_notification
from app.v2_0.HRMS.domain.models.leaves import Leaves
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.schemas.leaves_schemas import ApplyLeave
from app.v3_0.forms.add_leaves_form import add_leaves
from app.v3_0.schemas.form_schema import DropdownField, DropdownOption, DynamicForm
from app.v3_0.schemas.screen_schema import BuildScreen, DynamicTableSchema, TableColumns, DynamicListTileSchema, \
    TileData
from app.v3_0.service.tasks_services import map_to_model


def get_approver_list(user_id, db):
    ucb_user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()

    approver_data = []

    for a in ucb_user.approvers:
        data = get_approver_data(a, db)
        approver_data.append(DropdownOption(label=data.approver_name, value=[data.id]))

    return DropdownField(
        options=approver_data)


def build_apply_leave_form(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        # if leave_id:
        #     leave = db.query(Leaves).filter(Leaves.leave_id == leave_id).first()
        #     add_leaves.sections[0].row[0].fields[3].dropdown_field = get_approver_list(leave.user_id, db)
        add_leaves.sections[0].row[0].fields[3].dropdown_field = get_approver_list(user_id, db)

        return ResponseDTO(200, "Form plotted!", add_leaves)
    except HTTPException as e:
        return ResponseDTO(204, str(e), {})
    finally:
        db.close()


async def add_dynamic_leaves(new_leave: DynamicForm, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        msg = "Leave application submitted. Change in the number of leaves will be reflected after approval."
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
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
    finally:
        db.close()


def get_leaves_color_code(text):
    if text == 'REJECTED':
        return "0xFFE53935"
    elif text == 'APPROVED':
        return "0xFF4BB543"
    elif text == 'PENDING':
        return "0xFF345AFA"
    else:
        return "0xFFBDBDBD"


def fetch_my_leaves(buildScreen: BuildScreen, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            if buildScreen.isMobile is False:
                data = DynamicTableSchema(table_name="My Leaves",
                                          columns=[TableColumns(column_title="Leave Type", data_key="leave_type",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="From", data_key="start_date",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="To", data_key="end_date",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Approver", data_key="approver",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Leave Status", data_key="leave_status",
                                                                data_type=DataTypeEnum.status),
                                                   TableColumns(column_title="Show Details", data_key='show_details',
                                                                data_type=DataTypeEnum.button)])
            else:
                data = DynamicListTileSchema(screen_name="My Leaves",
                                             tile_data=TileData(title_key="leave_type", subtitle_key="date",
                                                                status_key="leave_status"))
            result = []
            my_leaves = db.query(Leaves).filter(Leaves.user_id == user_id).all()
            for leave in my_leaves:
                result.append(
                    {"leave_type": leave.leave_type.name, "id": leave.leave_id, "leave_reason": leave.leave_reason,
                     "start_date": leave.start_date.strftime("%d/%m/%Y"),
                     "end_date": leave.end_date.strftime("%d/%m/%Y"),
                     "date": f'{leave.start_date.strftime("%d/%m/%Y")} - {leave.end_date.strftime("%d/%m/%Y")}',
                     "approvers": get_approver_names(leave.approvers, db)[0],
                     "leave_status": leave.leave_status.name, "comment": leave.comment,
                     "status_color": get_leaves_color_code(leave.leave_status.name),
                     "show_details": {"button_name": "Show Details",
                                      "button_action": ButtonActionEnum.pop_up}})

            data.view_data = result

            if len(my_leaves) == 0:
                return ResponseDTO(200, "You have not applied for any leaves!", data)
            else:
                return ResponseDTO(200, "My Leaves fetched!", data)
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
    finally:
        db.close()


def get_user_name(leave, db):
    user = db.query(UserDetails).filter(UserDetails.user_id == leave.user_id).first()
    return user.first_name + " " + user.last_name


def fetch_pending_leaves(buildScreen: BuildScreen, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            if buildScreen.isMobile is False:
                data = DynamicTableSchema(table_name="Pending Leaves",
                                          columns=[TableColumns(column_title="Applicant Name", data_key="name",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Leave Type", data_key="leave_type",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="From", data_key="start_date",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="To", data_key="end_date",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Approver", data_key="approver",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Leave Status", data_key="leave_status",
                                                                data_type=DataTypeEnum.status),
                                                   TableColumns(column_title="Show Details", data_key='show_details',
                                                                data_type=DataTypeEnum.button)])
            else:
                data = DynamicListTileSchema(screen_name="My Leaves",
                                             tile_data=TileData(title_key="leave_type", subtitle_key="date",
                                                                status_key="leave_status"))
            result = []
            pending_leaves = db.query(Leaves).filter(Leaves.leave_status == LeaveStatus.PENDING).all()
            filtered_leaves = get_authorized_leave_requests(pending_leaves, user_id)

            if len(filtered_leaves) != 0:
                final_list = format_pending_leaves(filtered_leaves, db)
                for leave in final_list:
                    result.append(
                        {"name": leave.name, "leave_type": leave.leave_type.name, "id": leave.leave_id,
                         "leave_reason": leave.leave_reason,
                         "start_date": leave.start_date.strftime("%d/%m/%Y"),
                         "end_date": leave.end_date.strftime("%d/%m/%Y"),
                         "date": f'{leave.start_date.strftime("%d/%m/%Y")} - {leave.end_date.strftime("%d/%m/%Y")}',
                         "approvers": get_approver_names(leave.approvers, db)[0],
                         "leave_status": leave.leave_status.name, "comment": leave.comment,
                         "status_color": get_leaves_color_code(leave.leave_status.name),
                         "show_details": {"button_name": "Show Details",
                                          "button_action": ButtonActionEnum.pop_up}})
            data.view_data = result

            if len(pending_leaves) == 0:
                return ResponseDTO(200, "No pending leaves!", data)
            else:
                return ResponseDTO(200, "Leaves fetched!", data)
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
    finally:
        
        db.close()

# async def modify_leave_status(application_response, user_id, company_id, branch_id, db):
#     """Leaves are APPROVED or REJECTED using this API"""
#     try:
#         check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
#
#         if check is None:
#             leave_query = db.query(Leaves).filter(Leaves.leave_id == application_response.leave_id)
#             leave = leave_query.first()
#             status = LeaveStatus.REJECTED
#             if leave is None:
#                 return ResponseDTO(404, "Leave entry not found!", {})
#
#             if leave.is_leave_approved is True or leave.leave_status == LeaveStatus.REJECTED:
#                 return ResponseDTO(200, "Leave already updated!", leave)
#
#             if application_response.is_leave_approved is True:
#                 status = LeaveStatus.APPROVED
#                 update_user_leaves(leave, db)
#
#             application_response.leave_status = status
#             application_response.modified_by = user_id
#             application_response.modified_on = datetime.now()
#             leave_query.update(application_response.__dict__)
#             db.commit()
#
#             await send_leave_status_notification(application_response, user_id, company_id, branch_id, db)
#
#             return ResponseDTO(200, "Leave status updated!", {})
#         else:
#             return check
#
#
#     except HTTPException as e:
#
#         return ResponseDTO(204, str(e), {})
#
#     except ValueError as e:
#
#         return ResponseDTO(204, str(e), {})
#
#     except Exception as exc:
#
#         return ResponseDTO(204, str(exc), {})
#
#
# def withdraw_leave_func(leave_id: int, user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
#     try:
#         check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
#
#         if check is None:
#             leave_query = db.query(Leaves).filter(Leaves.leave_id == leave_id)
#             leave = leave_query.first()
#             leave_response = {}
#             if leave is None:
#                 return ResponseDTO(204, "Leave entry not found!", {})
#
#             if leave.is_leave_approved is True or leave.leave_status == LeaveStatus.REJECTED or leave.leave_status == LeaveStatus.APPROVED:
#                 return ResponseDTO(200, "Leave already updated!", leave)
#
#             leave_response["leave_status"] = LeaveStatus.WITHDRAWN
#             leave_response["modified_by"] = user_id
#             leave_response["modified_on"] = datetime.now()
#             leave_response["comment"] = "Leave withdrawn"
#             leave_query.update(leave_response)
#             db.commit()
#
#             return ResponseDTO(200, "Leave withdrawn successfully", {})
#         else:
#             return check
#
#     except Exception as exc:
#         db.rollback()
#         return ResponseDTO(204, str(exc), {})

from fastapi import Depends

from app.dto.dto_classes import ResponseDTO
from app.enums.designation_enum import DesignationEnum
from app.enums.screen_enums import DataTypeEnum
from app.infrastructure.database import get_db
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.application.service.employee_service import get_designation_name
from app.v2_0.HRMS.domain.models.user_auth import UsersAuth
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.models.user_finance import UserFinance
from app.v3_0.forms.add_employee_form import add_employee
from app.v3_0.forms.add_task_form import format_enum_member
from app.v3_0.schemas.form_schema import DropdownOption, DropdownField
from app.v3_0.schemas.screen_schema import BuildScreen, DynamicTableSchema, TableColumns, DynamicListTileSchema, \
    TileData
from app.v3_0.service.tasks_services import tasks_employee_dropdown


def employee_designation_dropdown(enums):
    """Format Enums and create options list"""
    dropdown_options = []
    for enum in enums:
        dropdown_options.append(
            DropdownOption(label=format_enum_member(enum.name), value=enum.value))
    return DropdownField(
        options=dropdown_options)


def build_add_employee_form(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        add_employee.sections[5].row[0].fields[0].dropdown_field = employee_designation_dropdown(DesignationEnum)
        add_employee.sections[5].row[1].fields[0].dropdown_field = tasks_employee_dropdown(branch_id, db)
        add_employee.sections[5].row[1].fields[1].dropdown_field = tasks_employee_dropdown(branch_id, db)

        return ResponseDTO(200, "Form plotted!", add_employee)
    except Exception as e:
        return ResponseDTO(204, str(e), {})
    finally:
        db.close()


def get_designation_color_code(text):
    if text == 'REJECTED':
        return "0xFFE53935"
    elif text == 'EMPLOYEE':
        return "0xFF4BB543"
    elif text == 'OWNER':
        return "0xFF345AFA"
    else:
        return "0xFFBDBDBD"


def employees_list(branch_id, db):
    employees_query = (
        db.query(UserDetails, UsersAuth, UserCompanyBranch, UserFinance)
        .join(UserCompanyBranch, UserDetails.user_id == UserCompanyBranch.user_id)
        .join(UsersAuth, UsersAuth.user_id == UserDetails.user_id)
        .join(UserFinance, UserFinance.user_id == UserDetails.user_id)
        .filter(UserCompanyBranch.branch_id == branch_id).order_by(UserDetails.user_id))

    result = []
    for details, auth, ucb, finance in employees_query:
        payroll = finance.basic_salary - finance.deduction
        result.append({"employee_id": auth.user_id,
                       "name": details.first_name + " " + details.last_name if details.first_name and details.last_name else "Invited User",
                       "user_contact": details.user_contact, "user_email": auth.user_email,
                       "designations": get_designation_name(ucb.designations),
                       "current_address": details.current_address, "payroll": payroll})
    return result


def fetch_all_employees(buildScreen: BuildScreen, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            if buildScreen.isMobile is False:
                data = DynamicTableSchema(table_name="Employees List",
                                          columns=[TableColumns(column_title="Name", data_key="name",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Employee ID", data_key="id",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Email", data_key="user_email",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Phone", data_key="user_contact",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Designation", data_key="designations",
                                                                data_type=DataTypeEnum.status)])
            else:
                data = DynamicListTileSchema(screen_name="Employees List",
                                             tile_data=TileData(title_key="name", subtitle_key="employee_id",
                                                                status_key="Designation"))
            employees_query = (
                db.query(UserDetails, UsersAuth, UserCompanyBranch, UserFinance)
                .join(UserCompanyBranch, UserDetails.user_id == UserCompanyBranch.user_id)
                .join(UsersAuth, UsersAuth.user_id == UserDetails.user_id)
                .join(UserFinance, UserFinance.user_id == UserDetails.user_id)
                .filter(UserCompanyBranch.branch_id == branch_id).order_by(UserDetails.user_id))

            result = []
            for details, auth, ucb, finance in employees_query:
                payroll = finance.basic_salary - finance.deduction
                result.append({"id": auth.user_id,
                               "name": details.first_name + " " + details.last_name if details.first_name and details.last_name else "Invited User",
                               "user_contact": details.user_contact, "user_email": auth.user_email,
                               "designations": get_designation_name(ucb.designations),
                               "status_color": get_designation_color_code(get_designation_name(ucb.designations)[0]),
                               "current_address": details.current_address, "payroll": payroll})
            data.view_data = result

            if len(result) == 0:
                return ResponseDTO(200, "You have not applied for any leaves!", data)
            else:
                return ResponseDTO(200, "My Leaves fetched!", data)
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
    finally:
        db.close()


def get_timesheet(buildScreen: BuildScreen, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            if buildScreen.isMobile is False:
                data = DynamicTableSchema(table_name="Employees List",
                                          columns=[TableColumns(column_title="Name", data_key="name",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Employee ID", data_key="id",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Email", data_key="user_email",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Phone", data_key="user_contact",
                                                                data_type=DataTypeEnum.text),
                                                   TableColumns(column_title="Designation", data_key="designations",
                                                                data_type=DataTypeEnum.status)])
            else:
                data = DynamicListTileSchema(screen_name="Employees List",
                                             tile_data=TileData(title_key="name", subtitle_key="employee_id",
                                                                status_key="Designation"))
            employees_query = (
                db.query(UserDetails, UsersAuth, UserCompanyBranch, UserFinance)
                .join(UserCompanyBranch, UserDetails.user_id == UserCompanyBranch.user_id)
                .join(UsersAuth, UsersAuth.user_id == UserDetails.user_id)
                .join(UserFinance, UserFinance.user_id == UserDetails.user_id)
                .filter(UserCompanyBranch.branch_id == branch_id).order_by(UserDetails.user_id))

            result = []
            for details, auth, ucb, finance in employees_query:
                payroll = finance.basic_salary - finance.deduction
                result.append({"id": auth.user_id,
                               "name": details.first_name + " " + details.last_name if details.first_name and details.last_name else "Invited User",
                               "user_contact": details.user_contact, "user_email": auth.user_email,
                               "designations": get_designation_name(ucb.designations),
                               "status_color": get_designation_color_code(get_designation_name(ucb.designations)[0]),
                               "current_address": details.current_address, "payroll": payroll})
            data.view_data = result

            if len(result) == 0:
                return ResponseDTO(200, "You have not applied for any leaves!", data)
            else:
                return ResponseDTO(200, "My Leaves fetched!", data)
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
    finally:
        db.close()

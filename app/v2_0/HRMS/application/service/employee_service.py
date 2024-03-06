"""Service layer for Employees"""
from datetime import datetime

from sqlalchemy import select

from app.dto.dto_classes import ResponseDTO
from app.enums.activity_status_enum import ActivityStatus
from app.enums.designation_enum import DesignationEnum
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.HRMS.application.service.ucb_service import add_employee_to_ucb
from app.v2_0.HRMS.application.service.user_service import add_user_details
from app.v2_0.HRMS.domain.models.branch_settings import BranchSettings
from app.v2_0.HRMS.domain.models.branches import Branches
from app.v2_0.HRMS.domain.models.user_auth import UsersAuth
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.models.user_finance import UserFinance
from app.v2_0.HRMS.domain.schemas.employee_schemas import GetEmployeeSalaries, UpdateActivityStatus
from app.v2_0.HRMS.domain.schemas.user_schemas import AddUser


def set_employee_details(new_employee, branch_id, db):
    """Sets employee details"""
    try:
        branch_settings = db.query(BranchSettings).filter(BranchSettings.branch_id == branch_id).first()
        employee_details = AddUser
        employee_details.first_name = ""
        employee_details.last_name = ""
        employee_details.middle_name = ""
        employee_details.medical_leaves = branch_settings.total_medical_leaves
        employee_details.casual_leaves = branch_settings.total_casual_leaves
        employee_details.activity_status = ActivityStatus.ACTIVE
        add_user_details(employee_details, new_employee.user_id, db)
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def assign_new_branch_to_existing_employee(employee, user, company_id, branch_id, db):
    """Adds the same employee to a different branch of the company"""
    add_employee_to_ucb(employee, user, company_id, branch_id, db)


def invite_employee(employee, user_id, company_id, branch_id, db):
    """Adds an employee in the db"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, None, db)

        if check is None:

            if employee.user_email is None:
                return ResponseDTO(204, "Please enter an email!", {})

            user = db.query(UsersAuth).filter(UsersAuth.user_email == employee.user_email).first()

            inviter = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()

            if user:
                user_company = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user.user_id).filter(
                    UserCompanyBranch.company_id != company_id).first
                if user_company:
                    return ResponseDTO(204, "User already belongs to a different company", {})
                ucb = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user.user_id).filter(
                    UserCompanyBranch.company_id == company_id).filter(UserCompanyBranch.branch_id == branch_id).first()
                if ucb:
                    return ResponseDTO(200, "User already belongs to this branch", {})
                assign_new_branch_to_existing_employee(employee, user, company_id, branch_id, db)

            else:
                new_employee = UsersAuth(user_email=employee.user_email, invited_by=inviter.user_email)
                db.add(new_employee)
                db.flush()
                add_employee_to_ucb(employee, new_employee, company_id, branch_id, db)
                set_employee_details(new_employee, branch_id, db)
                create_password_reset_code(employee.user_email, db)
                db.commit()

            return ResponseDTO(200, "Invite sent Successfully", {})
        else:
            db.rollback()
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


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


def fetch_employees(company_id, branch_id, user_id, db):
    """Returns all the employees belonging to a particular branch"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            result = employees_list(branch_id, db)
            return ResponseDTO(200, "Employees fetched!", result)
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), [])


def get_branch_name(branch_id, db):
    branch = db.query(Branches).filter(Branches.branch_id == branch_id).first()
    return branch.branch_name


def get_designation_name(designations):
    names = []
    for designation in designations:
        names.append(designation.name)
    return names


def fetch_employee_salaries(user_id, company_id, branch_id, db):
    """Fetches the salaries of employees"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            salaries_query = (select(UserCompanyBranch.designations, UserDetails.first_name,
                                     UserDetails.last_name, UserFinance.salary, UserFinance.deduction).select_from(
                UserCompanyBranch).join(UserFinance, UserCompanyBranch.user_id == UserFinance.user_id)
                              .join(UserDetails, UserCompanyBranch.user_id == UserDetails.user_id).filter(
                UserCompanyBranch.branch_id == branch_id)
                              .filter(UserCompanyBranch.designations != [DesignationEnum.OWNER]))

            salaries = db.execute(salaries_query)

            result = [
                GetEmployeeSalaries(name=salary.first_name + " " + salary.last_name,
                                    designations=get_designation_name(salary.designations),
                                    resultant_salary=salary.salary - salary.deduction)
                for salary in salaries
            ]
            if len(result) == 0:
                return ResponseDTO(200, "There are no employees in this branch!", {})
            return ResponseDTO(200, "Salaries fetched!", result)

        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), [])


def modify_activity_status(status: UpdateActivityStatus, user_id, company_id, branch_id, u_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            status_query = db.query(UserDetails).filter(UserDetails.user_id == u_id)
            status_query.update(
                {"modified_by": user_id, "modified_on": datetime.now(), "activity_status": status.activity_status})
            db.commit()
            return ResponseDTO(200, "Employee's activity status updated!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

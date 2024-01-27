"""Service layer for Employees"""

from sqlalchemy import select

from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.application.service.user_service import add_user_details
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist, add_employee_to_ucb
from app.v2_0.domain import models
from app.v2_0.domain.schema import AddUser, GetEmployees


def set_employee_details(new_employee, branch_id, db):
    """Sets employee details"""
    try:
        branch_settings = db.query(models.BranchSettings).filter(models.BranchSettings.branch_id == branch_id).first()
        employee_details = AddUser
        employee_details.first_name = None
        employee_details.last_name = None
        employee_details.medical_leaves = branch_settings.total_medical_leaves
        employee_details.casual_leaves = branch_settings.total_casual_leaves
        employee_details.activity_status = "ACTIVE"
        add_user_details(employee_details, new_employee.user_id, db)
    except Exception as exc:
        return ExceptionDTO("set_employee_details", exc)


def assign_new_branch_to_existing_employee(employee, user, company_id, branch_id, db):
    add_employee_to_ucb(employee, user, company_id, branch_id, db)
    msg = ""
    for role in employee.roles:
        msg = msg + role.name

    print(msg)
    # create_smtp_session(user.user_email, msg)


def invite_employee(employee, user_id, company_id, branch_id, db):
    """Adds an employee in the db"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            user = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == employee.user_email).first()
            inviter = db.query(models.UsersAuth).filter(models.UsersAuth.user_id == user_id).first()
            new_employee = models.UsersAuth(user_email=employee.user_email,
                                            invited_by=inviter.user_email)
            if user:
                assign_new_branch_to_existing_employee(employee, user, company_id, branch_id, db)

            else:
                db.add(new_employee)
                db.commit()
                db.refresh(new_employee)
                add_employee_to_ucb(employee, new_employee, company_id, branch_id, db)
                set_employee_details(new_employee, branch_id, db)
                create_password_reset_code(employee.user_email, db)

            return ResponseDTO(200, "Invite sent Successfully", {})
        else:
            return check
    except Exception as exc:
        return ExceptionDTO("invite_employee", exc)


def fetch_employees(branch_id, company_id, db):
    """Returns all the employees belonging to a particular branch"""
    try:
        company = db.query(models.Companies).filter(models.Companies.company_id == company_id).first()
        if company is None:
            return ResponseDTO(404, "Company not found!", {})

        branch = db.query(models.Branches).filter(models.Branches.branch_id == branch_id).first()
        if branch is None:
            return ResponseDTO(404, "Branch not found!", {})

        stmt = select(models.UserDetails.first_name, models.UserDetails.last_name, models.UserDetails.user_contact,
                      models.UserDetails.current_address, models.UserCompanyBranch.roles, models.UsersAuth.user_email,
                      models.UsersAuth.user_id).select_from(models.UserDetails).join(models.UserCompanyBranch,
                                                                                     models.UserDetails.user_id == models.UserCompanyBranch.user_id).join(
            models.UsersAuth, models.UsersAuth.user_id == models.UserDetails.user_id).filter(
            models.UserCompanyBranch.branch_id == branch_id)

        employees = db.execute(stmt)
        result = [GetEmployees(name=employee.first_name + " " + employee.last_name, user_contact=employee.user_contact,
                               roles=employee.roles, user_email=employee.user_email,
                               current_address=employee.current_address) for employee in employees]

        return ResponseDTO(200, "Employees fetched!", result)

    except Exception as exc:
        return ExceptionDTO("fetch_employees", exc)

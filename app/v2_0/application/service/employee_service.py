"""Service layer for Employees"""

from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.application.service.user_service import add_user_details
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist, add_employee_to_ucb
from app.v2_0.domain import models
from app.v2_0.domain.schema import AddUser


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
            return ResponseDTO(204, "Company not found!", {})

        branch = db.query(models.Branches).filter(models.Branches.branch_id == branch_id).first()
        if branch is None:
            return ResponseDTO(204, "Branch not found!", {})

        result = []
        employees = (db.query(models.UserCompanyBranch, models.UserDetails, models.UsersAuth)
                     .join(models.UserDetails, models.UserCompanyBranch.user_id == models.UserDetails.user_id)
                     .join(models.UsersAuth, models.UsersAuth.user_id == models.UserDetails.user_id)
                     .filter(models.UserCompanyBranch.company_id == company_id)
                     .filter(models.UserCompanyBranch.branch_id == branch_id).all())

        for employee in employees:
            employee_data = {
                "name": f"{employee.UserDetails.first_name} {employee.UserDetails.last_name}" if employee.UserDetails.first_name else None,
                "user_contact": employee.UserDetails.user_contact, "roles": employee.UserCompanyBranch.roles,
                "user_email": employee.UsersAuth.user_email, "current_address": employee.UserDetails.current_address,
                "employee_id": employee.UserDetails.user_id, "user_image": employee.UserDetails.user_image}
            result.append(employee_data)
        return ResponseDTO(200, "Employees fetched!", result)

    except Exception as exc:
        return ResponseDTO(204, str(exc), [])

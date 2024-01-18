"""Service layer for Employees"""
from datetime import datetime

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.application.service.user_service import add_user_details
from app.v2_0.domain import models
from app.v2_0.domain.schema import AddUser


def add_employee_to_ucb(employee, new_employee, company_id, branch_id, db):
    ucb_employee = models.UserCompanyBranch(user_id=new_employee.user_id, company_id=company_id, branch_id=branch_id,
                                            role=employee.role)
    db.add(ucb_employee)
    db.commit()


def set_employee_details(new_employee, db):
    employee_details = AddUser
    employee_details.first_name = None
    employee_details.last_name = None
    employee_details.medical_leaves = 12
    employee_details.casual_leaves = 3
    employee_details.activity_status = "ACTIVE"
    add_user_details(employee_details, new_employee.user_id, db)


def invite_employee(employee, user_id, company_id, branch_id, db):
    """Adds an employee in the db"""
    user = db.query(models.UsersAuth).filter(models.UsersAuth.user_id == user_id).first()
    new_employee = models.UsersAuth(user_email=employee.user_email, password="-", modified_by=user_id,
                                    invited_by=user.user_email)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    add_employee_to_ucb(employee, new_employee, company_id, branch_id, db)
    set_employee_details(new_employee, db)
    create_password_reset_code(employee.user_email, db)

    return ResponseDTO(200, "Invite sent Successfully", {})


# def fetch_employees(branch_id, db):
#     """Returns all the employees belonging to a particular branch"""
#     stmt = (select(models.UserDetails.first_name, models.UserDetails.last_name,
#                    models.UserDetails.user_contact,
#                    models.UserCompanyBranch.role)
#     .select_from(models.UserDetails).join(models.UserCompanyBranch,
#                                           models.UserDetails.user_id == models.UserCompanyBranch.user_id).filter(
#         models.UserCompanyBranch.branch_id == branch_id).filter(
#         models.UserCompanyBranch.role != "OWNER"))
#
#     stmt2 = (select(models.UsersAuth.user_email)
#     .select_from(models.UsersAuth).join(models.UserCompanyBranch,
#                                         models.UsersAuth.user_id == models.UserCompanyBranch.user_id).filter(
#         models.UserCompanyBranch.branch_id == branch_id).filter(
#         models.UserCompanyBranch.role != "OWNER"))
#
#     employees = db.execute(stmt)
#
#     return employees

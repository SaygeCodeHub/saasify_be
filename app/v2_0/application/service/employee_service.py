"""Service layer for Employees"""
from datetime import datetime

from sqlalchemy import select

from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.application.service.user_service import add_user_details
from app.v2_0.domain import models
from app.v2_0.domain.schema import AddUser, GetEmployees


def add_employee_to_ucb(employee, inviter, new_employee, company_id, branch_id, db):
    """Adds employee to the ucb table"""
    approvers_list = [inviter.user_id]
    try:
        if employee.approvers is not None:
            approvers_set = set(employee.approvers)
            approvers_set.add(inviter.user_id)
            approvers_list = list(approvers_set)

        ucb_employee = models.UserCompanyBranch(user_id=new_employee.user_id, company_id=company_id,
                                                branch_id=branch_id,
                                                roles=employee.roles, approvers=approvers_list)

        db.add(ucb_employee)
        db.commit()

    except Exception as exc:
        return ExceptionDTO("add_employee_to_ucb", exc)


def set_employee_details(new_employee, db):
    """Sets employee details"""
    try:
        employee_details = AddUser
        employee_details.first_name = None
        employee_details.last_name = None
        employee_details.medical_leaves = 12
        employee_details.casual_leaves = 3
        employee_details.activity_status = "ACTIVE"
        add_user_details(employee_details, new_employee.user_id, db)
    except Exception as exc:
        return ExceptionDTO("set_employee_details", exc)


def invite_employee(employee, user_id, company_id, branch_id, db):
    """Adds an employee in the db"""
    try:
        user = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == employee.user_email).first()
        if user is None:
            inviter = db.query(models.UsersAuth).filter(models.UsersAuth.user_id == user_id).first()
            new_employee = models.UsersAuth(user_email=employee.user_email, password="-", modified_by=user_id,
                                            invited_by=inviter.user_email)
            db.add(new_employee)
            db.commit()
            db.refresh(new_employee)
            add_employee_to_ucb(employee, inviter, new_employee, company_id, branch_id, db)
            set_employee_details(new_employee, db)
            create_password_reset_code(employee.user_email, db)
            return ResponseDTO(200, "Invite sent Successfully", {})
        else:
            return ResponseDTO(401, "Employee already invited!", user)

    except Exception as exc:
        return ExceptionDTO("invite_employee", exc)


def fetch_employees(branch_id, db):
    """Returns all the employees belonging to a particular branch"""
    try:
        stmt = select(models.UserDetails.first_name, models.UserDetails.last_name, models.UserDetails.user_contact,
                      models.UserDetails.current_address,
                      models.UserCompanyBranch.roles, models.UsersAuth.user_email,
                      models.UsersAuth.user_id).select_from(
            models.UserDetails).join(
            models.UserCompanyBranch,
            models.UserDetails.user_id == models.UserCompanyBranch.user_id).join(
            models.UsersAuth, models.UsersAuth.user_id == models.UserDetails.user_id).filter(models.UserCompanyBranch.branch_id == branch_id)

        employees = db.execute(stmt)
        result = [
            GetEmployees(
                name=employee.first_name + " " + employee.last_name,
                user_contact=employee.user_contact,
                roles=employee.roles,
                user_email=employee.user_email,
                current_address=employee.current_address
            )
            for employee in employees
        ]

        return ResponseDTO(200, "Employees fetched!", result)

    except Exception as exc:
        return ExceptionDTO("fetch_employees", exc)

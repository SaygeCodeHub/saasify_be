"""Service layer for Employees"""
from datetime import datetime

from sqlalchemy import select

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.domain import models


def invite_employee(employee, user_id, company_id, branch_id, db):
    """Adds an employee in the db"""
    user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    new_employee = models.Users(user_email=employee.user_email, password="-", modified_by=0,
                                invited_by=user.user_email,
                                activity_status="ACTIVE")
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    ucb_employee = models.UserCompanyBranch(user_id=new_employee.user_id, company_id=company_id, branch_id=branch_id,
                                            role=employee.role)
    db.add(ucb_employee)
    db.commit()
    create_password_reset_code(employee.user_email, db)

    return ResponseDTO(200, "Invite sent Successfully", {})


def modify_employee(employee, user_id, db):
    existing_employee_query = db.query(models.Users).filter(models.Users.user_id == user_id)
    employee.modified_by = user_id
    employee.modified_on = datetime.now()
    existing_employee_query.update(employee.__dict__)
    db.commit()

    return ResponseDTO(200, "Employee data updated!", {})


def fetch_employees(branch_id, db):
    """Returns all the employees belonging to a particular branch"""
    stmt = (select(models.Users.first_name, models.Users.last_name, models.Users.user_email, models.Users.user_contact,
                   models.UserCompanyBranch.role).select_from(models.Users).join(models.UserCompanyBranch,
                                                                                 models.Users.user_id == models.UserCompanyBranch.user_id)
            .filter(models.UserCompanyBranch.branch_id == branch_id).filter(
        models.UserCompanyBranch.role != "OWNER"))

    employees = db.execute(stmt)

    return employees

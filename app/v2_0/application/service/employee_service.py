"""Service layer for Employees"""
from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.domain import models


def invite_employee(user, db):
    """Adds an employee in the db"""
    new_employee = models.Users(user_email=user.user_email,password="-",modified_by=0,activity_status="ACTIVE")
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    create_password_reset_code(user.user_email, db)

    return ResponseDTO(200,"Invite sent Successfully",{})


def add_employee(employee, db):
    new_employee = models.UserCompanyBranch(**employee.model_dump())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return ResponseDTO(200,"Employee added to company!",new_employee)


"""Service layer for Employees"""
from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.domain import models_2


def add_employee(user, db):
    """Adds an employee in the db"""
    new_employee = models_2.Users(first_name=user.first_name,last_name=user.last_name,user_email=user.user_email,password="-",modified_by=0,activity_status="ACTIVE")
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    create_password_reset_code(user.user_email, db)

    return ResponseDTO("200","Invite sent Successfully",{})


def new_emp_in_company(employee,db):
    new_employee = models_2.UserCompanyBranch(**employee.model_dump())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return ResponseDTO("200","Employee added to company!",new_employee)


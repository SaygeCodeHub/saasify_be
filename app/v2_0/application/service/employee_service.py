"""Service layer for Employees"""

from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.application.service.user_service import add_user_details
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist, add_employee_to_ucb
from app.v2_0.domain.models.branch_settings import BranchSettings
from app.v2_0.domain.models.user_auth import UsersAuth
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.models.user_details import UserDetails
from app.v2_0.domain.schemas.employee_schemas import GetEmployees
from app.v2_0.domain.schemas.user_schemas import AddUser



def set_employee_details(new_employee, branch_id, db):
    """Sets employee details"""
    try:
        branch_settings = db.query(BranchSettings).filter(BranchSettings.branch_id == branch_id).first()
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
            user = db.query(UsersAuth).filter(UsersAuth.user_email == employee.user_email).first()
            inviter = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
            new_employee = UsersAuth(user_email=employee.user_email,
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


def fetch_employees(company_id, branch_id, db):
    """Returns all the employees belonging to a particular branch"""
    try:

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            stmt = select(UserDetails.first_name, UserDetails.last_name, UserDetails.user_contact,
                          UserDetails.current_address,
                          UserCompanyBranch.roles, UsersAuth.user_email,
                          UsersAuth.user_id).select_from(
                UserDetails).join(
                UserCompanyBranch,
                UserDetails.user_id == UserCompanyBranch.user_id).join(
                UsersAuth, UsersAuth.user_id == UserDetails.user_id).filter(
                UserCompanyBranch.branch_id == branch_id)

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
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), [])

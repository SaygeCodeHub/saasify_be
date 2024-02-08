"""Service layer for Employees"""
from sqlalchemy import select

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.application.service.ucb_service import add_owner_to_ucb
from app.v2_0.application.service.user_service import add_user_details
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.domain.models.branch_settings import BranchSettings
from app.v2_0.domain.models.branches import Branches
from app.v2_0.domain.models.enums import DesignationEnum, ActivityStatus
from app.v2_0.domain.models.user_auth import UsersAuth
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.models.user_details import UserDetails
from app.v2_0.domain.models.user_finance import UserFinance
from app.v2_0.domain.schemas.employee_schemas import GetEmployeeSalaries, GetEmployees
from app.v2_0.domain.schemas.user_schemas import AddUser


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
    add_owner_to_ucb(employee, user, company_id, branch_id, db)


def invite_employee(employee, user_id, company_id, branch_id, db):
    """Adds an employee in the db"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, None, db)

        if check is None:
            user = db.query(UsersAuth).filter(UsersAuth.user_email == employee.user_email).first()
            inviter = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
            ucb_user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user.user_id).first()

            if user and ucb_user:
                assign_new_branch_to_existing_employee(employee, user, company_id, branch_id, db)

            else:
                new_employee = UsersAuth(user_email=employee.user_email, invited_by=inviter.user_email)
                db.add(new_employee)
                db.flush()
                add_owner_to_ucb(employee, new_employee, company_id, branch_id, db)
                set_employee_details(new_employee, branch_id, db)
                create_password_reset_code(employee.user_email, db)
                db.commit()

            return ResponseDTO(200, "Invite sent Successfully", {})
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def fetch_employees(company_id, branch_id, user_id, db):
    """Returns all the employees belonging to a particular branch"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            employees_query = (
                db.query(UserDetails, UsersAuth, UserCompanyBranch)
                .join(UserCompanyBranch, UserDetails.user_id == UserCompanyBranch.user_id)
                .join(UsersAuth, UsersAuth.user_id == UserDetails.user_id)
                .filter(UserCompanyBranch.branch_id == branch_id))

            result = []
            for details, auth, ucb in employees_query:
                result = [GetEmployees(employee_id=auth.user_id,
                                       name=details.first_name + " " + details.last_name if details.first_name and details.last_name else None,
                                       user_contact=details.user_contact,
                                       designations=ucb.designations,
                                       user_email=auth.user_email,
                                       current_address=details.
                                       current_address)]

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
            salaries_query = select(UserCompanyBranch.designations, UserDetails.first_name,
                                    UserDetails.last_name, UserFinance.salary, UserFinance.deduction).select_from(
                UserCompanyBranch).join(UserFinance, UserCompanyBranch.user_id == UserFinance.user_id).join(UserDetails,
                                                                                                            UserCompanyBranch.user_id == UserDetails.user_id).filter(
                UserCompanyBranch.branch_id == branch_id).filter(
                UserCompanyBranch.designations != [DesignationEnum.OWNER])

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

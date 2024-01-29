"""Contains the code that acts as a utility to various files"""
from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.domain.models.branches import Branches
from app.v2_0.domain.models.companies import Companies
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch


def check_if_company_and_branch_exist(company_id, branch_id, db):
    company = db.query(Companies).filter(Companies.company_id == company_id).first()
    if company is None:
        return ResponseDTO(404, "Company not found!", {})

    branch = db.query(Branches).filter(Branches.branch_id == branch_id).first()
    if branch is None:
        return ResponseDTO(404, "Branch not found!", {})

    return None


def add_employee_to_ucb(employee, new_employee, company_id, branch_id, db):
    """Adds employee to the ucb table"""
    company = db.query(Companies).filter(Companies.company_id == company_id).first()
    approvers_list = [company.owner]
    try:
        if len(employee.approvers) != 0:
            approvers_set = set(employee.approvers)
            approvers_set.add(company.owner)
            approvers_list = list(approvers_set)

        ucb_employee = UserCompanyBranch(user_id=new_employee.user_id, company_id=company_id,
                                                branch_id=branch_id,
                                                roles=employee.roles, approvers=approvers_list)

        print(ucb_employee)

        db.add(ucb_employee)
        db.commit()

    except Exception as exc:
        return ExceptionDTO("add_employee_to_ucb", exc)

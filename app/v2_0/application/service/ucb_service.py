"""Service layer for UserCompanyBranch"""
from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.utility.app_utility import get_all_features
from app.v2_0.domain.models.companies import Companies
from app.v2_0.domain.models.enums import DesignationEnum
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch


def add_user_to_ucb(new_user, db):
    """Adds the data mapped to a user into db"""
    try:
        approver_list = [new_user.user_id]
        ucb = UserCompanyBranch(user_id=new_user.user_id, approvers=approver_list)
        db.add(ucb)
        db.commit()
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_employee_to_ucb(employee, new_employee, company_id, branch_id, db):
    """Adds employee to the ucb table"""
    company = db.query(Companies).filter(Companies.company_id == company_id).first()
    approvers_list = [company.owner]
    if employee.accessible_modules is None:
        employee.accessible_modules = [0]
    features_array = employee.accessible_features
    # try:
    if len(employee.approvers) != 0:
        approvers_set = set(employee.approvers)
        approvers_set.add(company.owner)
        approvers_list = list(approvers_set)

    if len(employee.accessible_features) == 0:
        features_array = get_all_features(employee.accessible_modules)

    print(new_employee)
    print(employee.__dict__)
    ucb_employee = UserCompanyBranch(user_id=new_employee.user_id, company_id=company_id,
                                     branch_id=branch_id,
                                     designations=employee.designations, approvers=approvers_list,
                                     accessible_modules=employee.accessible_modules,
                                     accessible_features=features_array)

    db.add(ucb_employee)
    db.commit()
    db.refresh(ucb_employee)
    print(f"after commit {ucb_employee.ucb_id}")

# except Exception as exc:
#     db.rollback()
#     return ResponseDTO(204, str(exc), {})


def add_company_to_ucb(new_company, user_id, db):
    """Adds the company to ucb table"""
    try:
        ucb_query = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id)
        ucb_query.update(
            {"company_id": new_company.company_id, "designations": [DesignationEnum.OWNER], "accessible_modules": [],
             "accessible_features": []})

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_init_branch_to_ucb(new_branch, user_id, company_id, db):
    """Adds the branch to Users company branch table"""
    ucb_query = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id)
    ucb_query.update({"branch_id": new_branch.branch_id})


def add_new_branch_to_ucb(new_branch, user_id, company_id, db):
    """Adds a new branch to an existing company"""
    b = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()
    approvers_list = b.approvers
    new_branch_in_ucb = UserCompanyBranch(user_id=user_id, company_id=company_id,
                                          branch_id=new_branch.branch_id,
                                          designations=[DesignationEnum.OWNER], approvers=approvers_list,
                                          accessible_modules=[], accessible_features=[])
    db.add(new_branch_in_ucb)

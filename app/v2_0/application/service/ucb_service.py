"""Service layer for UserCompanyBranch"""
from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.service.module_service import add_module
from app.v2_0.application.utility.app_utility import get_all_features
from app.v2_0.domain.models.companies import Companies
from app.v2_0.domain.models.enums import DesignationEnum, Modules
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.schemas.module_schemas import ModuleSchema


def add_owner_to_ucb(new_user, db):
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
    features_array = employee.accessible_features
    try:
        if len(employee.approvers) != 0:
            approvers_set = set(employee.approvers)
            approvers_set.add(company.owner)
            approvers_list = list(approvers_set)

        if len(employee.accessible_features) == 0:
            features_array = get_all_features(employee.accessible_modules)

        ucb_employee = UserCompanyBranch(user_id=new_employee.user_id, company_id=company_id,
                                         branch_id=branch_id,
                                         designations=employee.designations, approvers=approvers_list,
                                         accessible_modules=employee.accessible_modules,
                                         accessible_features=features_array)

        db.add(ucb_employee)

    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def add_company_to_ucb(new_company, user_id, db):
    """Adds the company to ucb table"""
    try:
        db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).update(
            {"company_id": new_company.company_id, "designations": [DesignationEnum.OWNER], "accessible_modules": [],
             "accessible_features": []})

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_branch_to_ucb(new_branch, user_id, company_id, db):
    """Adds the branch to Users company branch table"""
    try:
        b = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()

        if b.branch_id is None:
            db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).update(
                {"branch_id": new_branch.branch_id})

        elif b.branch_id != new_branch.branch_id:
            user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()
            approvers_list = user.approvers
            new_branch_in_ucb = UserCompanyBranch(user_id=user_id, company_id=company_id,
                                                  branch_id=new_branch.branch_id,
                                                  designations=[DesignationEnum.OWNER], approvers=approvers_list,
                                                  accessible_modules=[], accessible_features=[])
            db.add(new_branch_in_ucb)

        module = ModuleSchema
        module.modules = [Modules.HR]
        add_module(module, user_id, new_branch.branch_id, company_id, db)

    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})

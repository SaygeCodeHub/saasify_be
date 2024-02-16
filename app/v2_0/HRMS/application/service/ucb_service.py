"""Service layer for UserCompanyBranch"""
from app.v2_0.dto.dto_classes import ResponseDTO
from app.v2_0.HRMS.application.utility.app_utility import get_all_features
from app.v2_0.HRMS.domain.models.companies import Companies
from app.v2_0.enums import DesignationEnum, Modules, Features
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.schemas.employee_schemas import InviteEmployee


def add_user_to_ucb(new_user, db):
    """Adds the data mapped to a user into db"""
    try:
        approver_list = [new_user.user_id]

        ucb = UserCompanyBranch(user_id=new_user.user_id, approvers=approver_list)
        db.add(ucb)
        db.commit()
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_employee_to_ucb(employee: InviteEmployee, new_employee, company_id, branch_id, db):
    """Adds employee to the ucb table"""
    company = db.query(Companies).filter(Companies.company_id == company_id).first()
    approvers_list = []
    features_array = []
    modules_array = []
    if employee.accessible_modules is None:
        modules_array = [Modules.HR]
        features_array = get_all_features(modules_array)
    else:
        for module in employee.accessible_modules:
            for modules in Modules:
                if modules.value == module.module_id:
                    modules_array.append(modules)
            for feature in module.accessible_features:
                for features in Features:
                    if features.value == feature.feature_id:
                        features_array.append(features)
    if employee.approvers is None:
        approvers = [company.owner]
        approvers_list = list(approvers)
    elif len(employee.approvers) != 0:
        approvers_set = set(employee.approvers)
        if approvers_set.__contains__(company.owner) is False:
            approvers_set.add(company.owner)
        approvers_list = list(approvers_set)

    ucb_employee = UserCompanyBranch(user_id=new_employee.user_id, company_id=company_id,
                                     branch_id=branch_id,
                                     designations=employee.designations, approvers=approvers_list,
                                     accessible_modules=modules_array,
                                     accessible_features=features_array)

    db.add(ucb_employee)
    db.commit()
    db.refresh(ucb_employee)


def add_company_to_ucb(new_company, user_id, db):
    """Adds the company to ucb table"""
    try:
        accessible_modules = [Modules.HR]
        accessible_features = []
        for features in Features:
            if features.name.startswith(Modules.HR.name):
                accessible_features.append(features)
        ucb_query = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id)
        ucb_query.update(
            {"company_id": new_company.company_id, "designations": [DesignationEnum.OWNER],
             "accessible_modules": accessible_modules,
             "accessible_features": accessible_features})

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
    accessible_modules = [Modules.HR]
    accessible_features = []
    for features in Features:
        if features.name.startswith(Modules.HR.name):
            accessible_features.append(features)
    new_branch_in_ucb = UserCompanyBranch(user_id=user_id, company_id=company_id,
                                          branch_id=new_branch.branch_id,
                                          designations=[DesignationEnum.OWNER], approvers=approvers_list,
                                          accessible_modules=accessible_modules,
                                          accessible_features=accessible_features)
    db.add(new_branch_in_ucb)

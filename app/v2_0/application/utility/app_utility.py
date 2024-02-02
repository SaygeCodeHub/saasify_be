"""Contains the code that acts as a utility to various files"""
from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.domain.models.branches import Branches
from app.v2_0.domain.models.companies import Companies
from app.v2_0.domain.models.enums import Features
from app.v2_0.domain.models.module_subscriptions import ModuleSubscriptions
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
    features_array = employee.accessible_features
    try:
        if len(employee.approvers) != 0:
            approvers_set = set(employee.approvers)
            approvers_set.add(company.owner)
            approvers_list = list(approvers_set)

        if len(employee.accessible_features) == 0:
            features_array = get_all_features(employee.accessible_modules)

        ucb_employee = UserCompanyBranch(user_id=None, company_id=company_id,
                                         branch_id=branch_id,
                                         designations=employee.designations, approvers=approvers_list,
                                         accessible_modules=employee.accessible_modules,
                                         accessible_features=features_array)

        db.add(ucb_employee)

    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def add_owner_to_ucb(new_user, db):
    """Adds the data mapped to a user into db"""
    try:
        approver_list = [new_user.user_id]
        ucb = UserCompanyBranch(user_id=new_user.user_id, approvers=approver_list)
        db.add(ucb)
        db.commit()
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def get_all_features(module_array):
    features = []
    for module in module_array:
        for feature in list(Features.__members__):
            if feature.startswith(module.name):
                features.append(feature)
    return features


def add_module_to_ucb(branch_id, user_id, module_array, db):
    # try:
    query = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).filter(
        UserCompanyBranch.branch_id == branch_id)

    user = query.first()

    if len(module_array) == 0:
        subscribed_modules_set = []
        features_array = []
    else:
        # Fetches the currently subscribed modules
        subscribed_modules_set = set(user.accessible_modules)

        for module in module_array:
            subscribed_modules_set.add(module)

        features_array = get_all_features(subscribed_modules_set)

    query.update(
        {"accessible_modules": subscribed_modules_set,
         "accessible_features": features_array})
    db.commit()


# except Exception as exc:
#     return ResponseDTO(204, str(exc), {})


def add_company_to_ucb(new_company, user_id, db):
    """Adds the company to ucb table"""
    try:
        db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).update(
            {"company_id": new_company.company_id, "designations": ["OWNER"], "accessible_modules": [],
             "accessible_features": []})
        db.commit()
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_branch_to_ucb(new_branch, user_id, company_id, db):
    """Adds the branch to Users company branch table"""
    try:
        b = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()

        if b.branch_id is None:
            db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).update(
                {"branch_id": new_branch.branch_id})
            db.commit()
        elif b.branch_id != new_branch.branch_id:
            user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()
            approvers_list = user.approvers
            new_branch_in_ucb = UserCompanyBranch(user_id=user_id, company_id=company_id,
                                                  branch_id=new_branch.branch_id,
                                                  designations=["OWNER"], approvers=approvers_list,
                                                  accessible_modules=[], accessible_features=[])
            db.add(new_branch_in_ucb)
            db.commit()
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

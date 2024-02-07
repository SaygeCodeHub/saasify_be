"""Contains the code that acts as a utility to various files"""
from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.domain.models.branches import Branches
from app.v2_0.domain.models.companies import Companies
from app.v2_0.domain.models.enums import Features


def check_if_company_and_branch_exist(company_id, branch_id, user_id, db):
    company = db.query(Companies).filter(Companies.company_id == company_id).first()
    if company is None:
        return ResponseDTO(404, "Company not found!", {})

    branch = db.query(Branches).filter(Branches.branch_id == branch_id).first()
    if branch is None:
        return ResponseDTO(404, "Branch not found!", {})

    if user_id:
        ucb = db.query(UserCompanyBranch).filter(UserCompanyBranch.company_id == company_id).filter(
            UserCompanyBranch.branch_id == branch_id).filter(UserCompanyBranch.user_id == user_id).first()
        if ucb is None:
            return ResponseDTO(409, "Unauthorized user!", {})

    return None


def get_all_features(module_array):
    features = []
    for module in module_array:
        for feature in list(Features.__members__):
            if feature.startswith(module.name):
                features.append(feature)
    return features

"""Contains the code that acts as a utility to various files"""
from typing import Optional, List

from app.dto.dto_classes import ResponseDTO
from app.enums.features_enum import Features
from app.v2_0.HRMS.domain.models.branches import Branches
from app.v2_0.HRMS.domain.models.companies import Companies
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch


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


def ensure_optional_fields(self):
    for field in self.__annotations__:
        if field in self.__dict__ and self.__dict__[field] is None:
            if self.__annotations__[field] == str:
                setattr(self, field, "")
            if self.__annotations__[field] == Optional[str]:
                setattr(self, field, "")
            elif self.__annotations__[field] == List:
                setattr(self, field, [])
            elif self.__annotations__[field] == Optional[List]:
                setattr(self, field, [])
            elif self.__annotations__[field] == dict:
                setattr(self, field, {})
            else:
                setattr(self, field, None)

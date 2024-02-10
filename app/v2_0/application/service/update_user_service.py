"""Service layer for Update Users"""
from datetime import datetime

from fastapi import Depends

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.password_handler.pwd_encrypter_decrypter import hash_pwd
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.application.service.ucb_service import add_user_to_ucb, add_employee_to_ucb
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.domain.models.branch_settings import BranchSettings
from app.v2_0.domain.models.companies import Companies
from app.v2_0.domain.models.leaves import Leaves
from app.v2_0.domain.models.user_auth import UsersAuth
from app.v2_0.domain.models.user_bank_details import UserBankDetails
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.models.user_details import UserDetails
from app.v2_0.domain.models.user_documents import UserDocuments
from app.v2_0.domain.models.user_finance import UserFinance
from app.v2_0.domain.models.user_official_details import UserOfficialDetails
from app.v2_0.domain.schemas.employee_schemas import InviteEmployee
from app.v2_0.domain.schemas.user_schemas import GetAadharDetails, \
    GetPassportDetails, GetPersonalInfo, UpdateUser, UserBankDetailsSchema, UserOfficialSchema, GetUserOfficialSchema, \
    GetUserFinanceSchema, GetUserBankDetailsSchema, PersonalInfo
from app.v2_0.infrastructure.database import get_db


def user_update_func(user: UpdateUser, user_id, company_id, branch_id, u_id, db=Depends(get_db)):
    """Updates a User"""

    check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
    print(check)
    if u_id == "" or user_id is None:
        """Add employee"""
        if user.personal_info.user_email is None:
            return ResponseDTO(400, "Email is required!", {})
        else:
            """email validation"""
            email_exist = db.query(UsersAuth).filter(UsersAuth.user_email == user.personal_info.user_email).first()
            if email_exist:
                return ResponseDTO(204, "User with this email already exists", {})

            """contact Validation"""
            if user.personal_info.user_contact is not None:
                contact_exists = db.query(UserDetails).filter(
                    UserDetails.user_contact == user.personal_info.user_contact).filter(
                    UserDetails.user_id != u_id).first()
                if contact_exists:
                    return ResponseDTO(409, "User with this contact already exists!", contact_exists)

            user_auth = db.query(UsersAuth).filter(UsersAuth.user_email == user.personal_info.user_email).first()
            if user_auth:
                ucb = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_auth.user_id).filter(
                    UserCompanyBranch.branch_id == branch_id).first()
                if ucb:
                    return ResponseDTO(204, "User with this email already exists in this branch!", {})
                else:
                    company = db.query(Companies).filter(Companies.company_id == company_id).first()
                    approvers_list = [company.owner]
                    # if employee.accessible_modules is None:
                    #     employee.accessible_modules = [0]
                    # features_array = employee.accessible_features
                    # # try:
                    # if employee.approvers is None:
                    #     approvers = [company.owner]
                    #     approvers_list = list(approvers)
                    # elif len(employee.approvers) != 0:
                    #     approvers_set = set(employee.approvers)
                    #     approvers_set.add(company.owner)
                    #     approvers_list = list(approvers_set)
                    # if employee.accessible_features is None:
                    #     features_array = get_all_features(employee.accessible_modules)
                    # elif len(employee.accessible_features) == 0:
                    #     features_array = get_all_features(employee.accessible_modules)
                    # new_ucb = UserCompanyBranch(user_id=user_auth.user_id, company_id=company_id, branch_id=branch_id,
                    #                             designation=user.official.designations,
                    #                             approvers=user.official.approvers,
                    #                             accessible_modules=user.official.accessible_modules,
                    #                             accessible_features=user.official.accessible_features)

    else:
        """update Existing user"""

    if check is not None:
        return check

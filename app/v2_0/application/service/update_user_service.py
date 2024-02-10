"""Service layer for Update Users"""

from fastapi import Depends

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.domain.models.companies import Companies
from app.v2_0.domain.models.enums import Features
from app.v2_0.domain.models.user_auth import UsersAuth
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.models.user_details import UserDetails
from app.v2_0.domain.schemas.employee_schemas import InviteEmployee
from app.v2_0.domain.schemas.user_schemas import UpdateUser
from app.v2_0.infrastructure.database import get_db


def user_update_func(user: UpdateUser, user_id, company_id, branch_id, u_id, db=Depends(get_db)):
    """Updates a User"""
    check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
    print(check)
    if u_id == "" or user_id is None:
        print("add emp")
        """Add employee"""
        if user.personal_info.user_email is None:
            print("email==null")
            return ResponseDTO(400, "Email is required!", {})
        else:
            """email validation"""
            email_exist = db.query(UsersAuth).filter(UsersAuth.user_email == user.personal_info.user_email).first()
            if email_exist:
                print("email exists")
                return ResponseDTO(204, "User with this email already exists", {})

            """contact Validation"""
            if user.personal_info.user_contact is not None:
                print("contact not null")
                contact_exists = db.query(UserDetails).filter(
                    UserDetails.user_contact == user.personal_info.user_contact).filter(
                    UserDetails.user_id != u_id).first()
                if contact_exists:
                    print("contact exists")
                    return ResponseDTO(409, "User with this contact already exists!", contact_exists)

            user_auth = db.query(UsersAuth).filter(UsersAuth.user_email == user.personal_info.user_email).first()
            if user_auth:
                print("user_auth exists")
                ucb = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_auth.user_id).filter(
                    UserCompanyBranch.branch_id == branch_id).first()
                if ucb:
                    print("ucb exists")
                    return ResponseDTO(204, "User with this email already exists in this branch!", {})
                else:
                    print("ucb not exists")
                    company = db.query(Companies).filter(Companies.company_id == company_id).first()
                    print(company.owner)
                    approvers_list = [company.owner]
                    if user.official.accessible_modules is None:
                        user.official.accessible_modules = [0]
                    features_array = user.official.accessible_features
                    if user.official.approvers is None:
                        approvers = [company.owner]
                        approvers_list = list(approvers)
                    elif len(user.official.approvers) != 0:
                        approvers_set = set(user.official.approvers)
                        approvers_set.add(company.owner)
                        approvers_list = list(approvers_set)
                    if user.official.accessible_features is None:
                        features_array = []
                        for module in user.official.accessible_modules:
                            for feature in list(Features.__members__):
                                if feature.startswith(str(module)):
                                    features_array.append(feature)
                    elif len(user.official.accessible_features) == 0:
                        features_array = []
                        for module in user.official.accessible_modules:
                            for feature in list(Features.__members__):
                                if feature == module:
                                    features_array.append(feature)
                    print("features_array", features_array)
                    print("approvers_list", approvers_list)
                    print(" user.official.accessible_modules", user.official.accessible_modules)
                    new_ucb = UserCompanyBranch(user_id=user_auth.user_id, company_id=company_id, branch_id=branch_id,
                                                designation=user.official.designations,
                                                approvers=approvers_list,
                                                accessible_modules=user.official.accessible_modules,
                                                accessible_features=features_array)
                    db.add(new_ucb)
                    db.flush()
                    db.rollback()
            else:
                print("user_auth not exists")
                inviter = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
                print("inviter", inviter)
                new_employee = UsersAuth(user_email=user.personal_info.user_email, invited_by=inviter.user_email)
                db.add(new_employee)
                print("add new employee")

                ucb_emp = InviteEmployee
                ucb_emp.approvers = user.official.approvers
                ucb_emp.designations = user.official.designations
                ucb_emp.accessible_modules = user.official.accessible_modules
                ucb_emp.accessible_features = user.official.accessible_features
                # add_employee_to_ucb(ucb_emp, new_employee, company_id, branch_id, db)
                db.add(user_auth)
                db.flush()

    else:
        """update Existing user"""

    if check is not None:
        return check

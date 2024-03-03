"""Service layer for building forms and tables"""
from datetime import datetime

from app.dto.dto_classes import ResponseDTO
from app.utility.app_utility import check_if_company_and_branch_exist, get_value
from app.v2_0.HRMS.domain.models.announcements import Announcements
from app.v2_0.HRMS.domain.models.companies import Companies
from app.v2_0.HRMS.domain.models.user_auth import UsersAuth
from app.v2_0.HRMS.domain.models.user_bank_details import UserBankDetails
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.models.user_documents import UserDocuments
from app.v2_0.HRMS.domain.models.user_finance import UserFinance
from app.v2_0.HRMS.domain.models.user_official_details import UserOfficialDetails
from app.v2_0.HRMS.domain.schemas.module_schemas import FeaturesMap, ModulesMap
from app.v2_0.HRMS.domain.schemas.user_schemas import GetPersonalInfo, GetAadharDetails, GetPassportDetails, \
    GetUserFinanceSchema, GetUserBankDetailsSchema, GetUserOfficialSchema
from app.v3_0.schemas.form_schema import DynamicForm
from app.v3_0.service.home_screen_service import get_title, calculate_value, check_if_statistics, get_is_view, \
    get_build_screen_endpoint


def add_dynamic_announcements(announcement: DynamicForm, user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if check is None:
            new_announcement = Announcements(company_id=company_id,
                                             due_date=get_value("due_date", announcement),
                                             description=get_value("description", announcement))
            # print(new_announcement.__dict__)
            db.add(new_announcement)
            db.commit()
            return ResponseDTO(200, "Announcement added!", {})
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def change_dynamic_announcement_data(announcement: DynamicForm, user_id, company_id, branch_id, announcement_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if check is None:
            announcement_query = db.query(Announcements).filter(Announcements.announcement_id == announcement_id)
            announcement_query.update(
                {"due_date": get_value("due_date", announcement), "description": get_value("description", announcement),
                 "is_active": get_value("is_active", announcement),
                 "modified_by": user_id,
                 "modified_on": datetime.now()})
            db.commit()
            # print(get_value("is_active", announcement))
            return ResponseDTO(200, "Announcement updated!", {})
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def fetch_by_id(u_id, user_id, company_id, branch_id, db):
    """Fetches a user by his id"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, None, db)

        if check is not None:
            return check

        else:
            user = db.query(UserDetails).filter(UserDetails.user_id == u_id).first()

            if user is None:
                return ResponseDTO(404, "User not found!", {})

            user_details = {}

            user_auth = db.query(UsersAuth).filter(UsersAuth.user_id == u_id).first()
            user_doc = db.query(UserDocuments).filter(UserDocuments.user_id == u_id).first()
            user_finances = db.query(UserFinance).filter(UserFinance.user_id == u_id).first()
            user_bank = db.query(UserBankDetails).filter(UserBankDetails.user_id == u_id).first()
            user_official = db.query(UserOfficialDetails).filter(UserOfficialDetails.user_id == u_id).first()
            ucb = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == u_id).first()
            company = db.query(Companies).filter(Companies.company_id == ucb.company_id).first()

            user.__dict__["user_email"] = user_auth.user_email
            user_details["personal_info"] = GetPersonalInfo(**user.__dict__ if user else {})
            official = user_official.__dict__ if user_official else {}
            accessible_modules = []
            can_edit = True
            if user_id == u_id:
                if user_id == company.owner:
                    can_edit = True
                else:
                    can_edit = False

            for acm in ucb.accessible_modules:
                accessible_features = []
                for features in ucb.accessible_features:
                    if features.name.startswith(acm.name):
                        accessible_features.append(FeaturesMap(feature_key=features.name, feature_id=features.value,
                                                               title=get_title(features.name),
                                                               icon="",
                                                               value=calculate_value(
                                                                   features.name, user_id, company_id, branch_id, db),
                                                               is_statistics=check_if_statistics(features.name),
                                                               is_view=get_is_view(features.name),
                                                               build_screen_endpoint=get_build_screen_endpoint(
                                                                   features.name)))
                accessible_modules.append(
                    ModulesMap(module_key=acm.name, module_id=acm.value, title=acm.name, icon="",
                               accessible_features=accessible_features))

            official.update(
                {"accessible_modules": accessible_modules if ucb else [], "approvers": ucb.approvers if ucb else [],
                 "designations": ucb.designations if ucb else [],
                 "can_edit": can_edit})
            user_details.update({"documents": {
                "aadhar": GetAadharDetails(**user_doc.__dict__ if user_doc else {}),
                "passport": GetPassportDetails(**user_doc.__dict__ if user_doc else {})}})
            user_details.update(
                {"financial": {"finances": GetUserFinanceSchema(**user_finances.__dict__ if user_finances else {}),
                               "bank_details": GetUserBankDetailsSchema(**user_bank.__dict__ if user_bank else {})}})
            user_details["official"] = GetUserOfficialSchema(**official if official else {})
            user_details["financial"]["finances"].__dict__.update(
                {"can_edit": can_edit})

        return ResponseDTO(200, "User fetched!", user_details)

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

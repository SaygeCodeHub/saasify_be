"""Service layer for Users"""
from datetime import datetime

from app.v2_0.dto.dto_classes import ResponseDTO
from app.v2_0.HRMS.application.password_handler.pwd_encrypter_decrypter import hash_pwd
from app.v2_0.HRMS.application.service.home_screen_service import calculate_value, check_if_statistics, get_title
from app.v2_0.HRMS.application.service.ucb_service import add_user_to_ucb
from app.v2_0.HRMS.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.branch_settings import BranchSettings
from app.v2_0.HRMS.domain.models.companies import Companies
from app.v2_0.HRMS.domain.models.leaves import Leaves
from app.v2_0.HRMS.domain.models.user_auth import UsersAuth
from app.v2_0.HRMS.domain.models.user_bank_details import UserBankDetails
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.models.user_documents import UserDocuments
from app.v2_0.HRMS.domain.models.user_finance import UserFinance
from app.v2_0.HRMS.domain.models.user_official_details import UserOfficialDetails
from app.v2_0.HRMS.domain.schemas.module_schemas import ModulesMap, FeaturesMap
from app.v2_0.HRMS.domain.schemas.user_schemas import GetAadharDetails, \
    GetPassportDetails, GetPersonalInfo, GetUserOfficialSchema, \
    GetUserFinanceSchema, GetUserBankDetailsSchema, UserBankDetailsSchema, UserOfficialSchema, PersonalInfo


def add_user_details(user, user_id, db):
    """Adds user details in the db"""
    try:
        user_details = UserDetails(user_id=user_id, first_name=user.first_name, last_name=user.last_name,
                                   activity_status=user.activity_status, medical_leaves=user.medical_leaves,
                                   casual_leaves=user.casual_leaves)
        db.add(user_details)

        # Creates an entry in the documents table for the corresponding user_id
        user_docs = UserDocuments(user_id=user_id)
        db.add(user_docs)

        # Creates an entry in the finance table for the corresponding user_id
        user_finance = UserFinance(user_id=user_id)
        db.add(user_finance)

    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def add_user(user, db):
    """Adds a user into the database"""
    try:
        user_email_exists = db.query(UsersAuth).filter(
            UsersAuth.user_email == user.user_email).first()

        if user_email_exists:
            return ResponseDTO(403, "User with this email already exists", {})
        hashed_pwd = hash_pwd(user.password)
        user.password = hashed_pwd
        new_user = UsersAuth(user_email=user.user_email, password=user.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        add_user_details(user, new_user.user_id, db)
        add_user_to_ucb(new_user, db)

        return ResponseDTO(200, "User created successfully",
                           {"user_id": new_user.user_id, "name": user.first_name + " " + user.last_name, "company": []})

    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def get_designations(user_id, db):
    user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()
    return user.designations


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
            user_details["designations"] = ucb.designations if ucb else []
            user_details["accessible_modules"] = ucb.accessible_modules if ucb else []
            user_details["accessible_features"] = ucb.accessible_features if ucb else []
            user_details["approvers"] = ucb.approvers if ucb else []
            user_details["personal_info"] = GetPersonalInfo(**user.__dict__ if user else {})
            official = user_official.__dict__ if user_official else {}

            accessible_modules = []

            for acm in ucb.accessible_modules:
                accessible_modules.append(
                    ModulesMap(module_key=acm.name, module_id=acm.value, title=acm.name, icon="", accessible_features=[
                        FeaturesMap(feature_key=af.name, feature_id=af.value, title=get_title(af.name), icon="",
                                    value=calculate_value(
                                        af.name, user_id, company_id, branch_id, db),
                                    is_statistics=check_if_statistics(af.name))
                        for af in ucb.accessible_features]))
            official.update(
                {"accessible_modules": accessible_modules if ucb else [], "approvers": ucb.approvers if ucb else [],
                 "designations": ucb.designations if ucb else []})
            user_details.update({"documents": {
                "aadhar": GetAadharDetails(**user_doc.__dict__ if user_doc else {}),
                "passport": GetPassportDetails(**user_doc.__dict__ if user_doc else {})}})
            user_details.update(
                {"financial": {"finances": GetUserFinanceSchema(**user_finances.__dict__ if user_finances else {}),
                               "bank_details": GetUserBankDetailsSchema(**user_bank.__dict__ if user_bank else {})}})
            user_details["official"] = GetUserOfficialSchema(**official.__dict__ if official else {})
            user_details["official"].__dict__.update({"can_edit": True if user_id == company.owner else False})
            user_details["financial"]["finances"].__dict__.update(
                {"can_edit": True if user_id == company.owner else False})

        return ResponseDTO(200, "User fetched!", user_details)

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def update_personal_info(personal_data, user_query, user_id):
    # Deleting the 'user_email' field from personal_data dictionary because the UserDetails table does not contain email column
    del personal_data.__dict__["user_email"]

    personal_data.__dict__["modified_on"] = datetime.now()
    personal_data.__dict__["modified_by"] = user_id
    user_query.update(personal_data.__dict__)


def update_user_documents(docs_data, u_id, user_id, db):
    # Unpacking the 2 dictionaries - aadhar and passport and storing them in a new dictionary
    new_docs_data = {**docs_data.aadhar.__dict__, **docs_data.passport.__dict__,
                     "modified_on": datetime.now(), "modified_by": user_id}
    aadhar_query = None
    pan_query = None
    passport_query = None
    if new_docs_data["aadhar_number"] is not None:
        aadhar_query = db.query(UserDocuments).filter(
            UserDocuments.aadhar_number == new_docs_data["aadhar_number"]).filter(
            UserDocuments.user_id != u_id).first()
    if new_docs_data["pan_number"] is not None:
        pan_query = db.query(UserDocuments).filter(UserDocuments.pan_number == new_docs_data["pan_number"]).filter(
            UserDocuments.user_id != u_id).first()
    if new_docs_data["passport_num"] is not None:
        passport_query = db.query(UserDocuments).filter(
            UserDocuments.passport_num == new_docs_data["passport_num"]).filter(
            UserDocuments.user_id != u_id).first()

    if aadhar_query and pan_query and passport_query is not None:
        resp = validate_docs(aadhar_query, pan_query, passport_query)
        if resp is not None:
            return resp

    docs_query = db.query(UserDocuments).filter(UserDocuments.user_id == u_id)
    docs_query.update(new_docs_data)

    return None


def update_user_bank_info(bank_data: UserBankDetailsSchema, u_id, db):
    ifsc_code = db.query(UserBankDetails).filter(UserBankDetails.ifsc_code == bank_data.ifsc_code).filter(
        UserBankDetails.user_id != u_id).first()
    account_number = db.query(UserBankDetails).filter(
        UserBankDetails.account_number == bank_data.account_number).filter(UserBankDetails.user_id != u_id).first()
    if ifsc_code:
        if ifsc_code.user_id != u_id:
            return ResponseDTO(409, "This ifsc code already belongs to someone else", {})
    if account_number:
        if account_number.user_id != u_id:
            return ResponseDTO(409, "This account number already belongs to someone else", {})

    bank_update = db.query(UserBankDetails).filter(UserBankDetails.user_id == u_id)
    bank_update.update({"bank_name": bank_data.bank_name,
                        "account_number": bank_data.account_number, "ifsc_code": bank_data.ifsc_code,
                        "branch_name": bank_data.branch, "account_type": bank_data.account_type,
                        "country": bank_data.country, "modified_on": datetime.now()})

    return None


def update_user_official_info(official_data: UserOfficialSchema, u_id, user_id, db):
    official_data.modified_on = datetime.now()
    official_data.modified_by = user_id

    docs_query = db.query(UserOfficialDetails).filter(UserOfficialDetails.user_id == u_id).first()
    docs_query.doj = official_data.doj
    docs_query.department_head = official_data.department_head
    docs_query.reporting_manager = official_data.reporting_manager
    docs_query.job_confirmation = official_data.job_confirmation
    docs_query.current_location = official_data.current_location
    docs_query.modified_on = datetime.now()
    docs_query.modified_by = user_id

    return None


def store_user_official_info(official_data: UserOfficialSchema, u_id, user_id, db):
    official_data.modified_on = datetime.now()
    official_data.modified_by = user_id

    official = UserOfficialDetails(doj=official_data.doj, department_head=official_data.department_head,
                                   reporting_manager=official_data.reporting_manager,
                                   job_confirmation=official_data.job_confirmation, user_id=u_id,
                                   current_location=official_data.current_location,
                                   modified_on=datetime.now(), modified_by=user_id)
    db.add(official)

    return None


def update_user_finance(finance_data, u_id, user_id, db):
    finance_data.__dict__["modified_on"] = datetime.now()
    finance_data.__dict__["modified_by"] = user_id

    finance_query = db.query(UserFinance).filter(UserFinance.user_id == u_id).first()
    finance_query.modified_on = datetime.now()
    finance_query.modified_by = user_id
    finance_query.basic_salary = finance_data.basic_salary
    finance_query.BOA = finance_data.BOA
    finance_query.bonus = finance_data.bonus
    finance_query.PF = finance_data.PF
    finance_query.performance_bonus = finance_data.performance_bonus
    finance_query.gratuity = finance_data.gratuity
    finance_query.deduction = finance_data.deduction
    finance_query.fixed_monthly_gross = finance_data.fixed_monthly_gross
    finance_query.total_annual_gross = finance_data.total_annual_gross
    db.commit()


def store_personal_info(personal_data: PersonalInfo, user_id, branch_id, db):
    if personal_data.user_contact is not None:
        user_contact = db.query(UserDetails).filter(
            UserDetails.user_contact == personal_data.user_contact).first()
        if user_contact:
            return ResponseDTO(409, "This contact already belongs to someone else", {})
    del personal_data.__dict__["user_email"]
    branch_settings = db.query(BranchSettings).filter(BranchSettings.branch_id == branch_id).first()
    personal_data.__dict__["user_id"] = user_id
    personal_data.casual_leaves = branch_settings.total_casual_leaves
    personal_data.medical_leaves = branch_settings.total_medical_leaves
    new_employee = UserDetails(**personal_data.__dict__)
    db.add(new_employee)

    return None


def validate_docs(aadhar_query, pan_query, passport_query):
    aadhar = aadhar_query
    pan = pan_query
    passport_num = passport_query
    if aadhar is not None:
        return ResponseDTO(409, "This aadhar number already belongs to someone else", {})
    if pan is not None:
        return ResponseDTO(409, "This pan number already belongs to someone else", {})
    if passport_num is not None:
        return ResponseDTO(409, "This passport number already belongs to someone else", {})


def store_user_documents(docs_data, user_id, db):
    new_docs_data = {**docs_data.aadhar.__dict__, **docs_data.passport.__dict__,
                     "user_id": user_id}
    aadhar_query = None
    pan_query = None
    passport_query = None
    if new_docs_data["aadhar_number"] is not None:
        aadhar_query = db.query(UserDocuments).filter(
            UserDocuments.aadhar_number == new_docs_data["aadhar_number"]).first()
    if new_docs_data["pan_number"] is not None:
        pan_query = db.query(UserDocuments).filter(UserDocuments.pan_number == new_docs_data["pan_number"]).first()
    if new_docs_data["passport_num"] is not None:
        passport_query = db.query(UserDocuments).filter(
            UserDocuments.passport_num == new_docs_data["passport_num"]).first()

    if aadhar_query and pan_query and passport_query is not None:
        resp = validate_docs(aadhar_query, pan_query, passport_query)
        if resp is not None:
            return resp
    docs = UserDocuments(**new_docs_data)
    db.add(docs)

    return None


def store_user_bank_data(bank_details: UserBankDetailsSchema, user_id, db):
    bank_details.modified_on = datetime.now()
    ifsc_code = db.query(UserBankDetails).filter(UserBankDetails.ifsc_code == bank_details.ifsc_code).first()
    account_number = db.query(UserBankDetails).filter(
        UserBankDetails.account_number == bank_details.account_number).first()
    resp = validate_bank_data(ifsc_code, account_number)
    if resp is not None:
        return resp
    new_bank_data = UserBankDetails(user_id=user_id, bank_name=bank_details.bank_name,
                                    account_number=bank_details.account_number, ifsc_code=bank_details.ifsc_code,
                                    branch_name=bank_details.branch, account_type=bank_details.account_type,
                                    country=bank_details.country, modified_on=datetime.now())
    db.add(new_bank_data)

    return None


def validate_bank_data(ifsc_code, account_number):
    ifsc_code = ifsc_code
    account_number = account_number

    if ifsc_code:
        return ResponseDTO(409, "This ifsc code already belongs to someone else", {})
    if account_number:
        return ResponseDTO(409, "This account number already belongs to someone else", {})


def store_user_finance(finance_data, user_id, db):
    data = UserFinance(user_id=user_id, basic_salary=finance_data.basic_salary,
                       BOA=finance_data.BOA, bonus=finance_data.bonus, PF=finance_data.PF,
                       performance_bonus=finance_data.performance_bonus, gratuity=finance_data.gratuity,
                       deduction=finance_data.deduction, fixed_monthly_gross=finance_data.fixed_monthly_gross,
                       total_annual_gross=finance_data.total_annual_gross, modified_on=datetime.now(), )
    db.add(data)


def update_leave_approvers(approvers_list, user_id, db):
    leave_query = db.query(Leaves).filter(Leaves.user_id == user_id)
    leave_query.update({"approvers": approvers_list})
    db.commit()


def update_approver(approver, user_id, company_id, branch_id, db):
    """Adds an approver to the list of approvers of a user"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, None, db)
        if check is None:
            flag = True
            user_query = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id)
            user = user_query.first()

            if user is None:
                return ResponseDTO(404, "User not found", {})

            company = db.query(Companies).filter(Companies.company_id == user.company_id).first()

            approvers_list = approver.approvers

            for a in approvers_list:
                if a != company.owner:
                    flag = False
                else:
                    flag = True

            if flag is False or len(approvers_list) == 0:
                approvers_list.append(company.owner)

            approver.approvers = approvers_list

            user_query.update(approver.__dict__)
            db.commit()

            update_leave_approvers(approvers_list, user_id, db)

            return ResponseDTO(200, "Approvers updated!", {})
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

"""Service layer for Update Users"""
from datetime import datetime
from typing import List

from fastapi import Depends

from app.v2_0.dto.dto_classes import ResponseDTO
from app.v2_0.HRMS.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.companies import Companies
from app.v2_0.enums import Features, Modules
from app.v2_0.HRMS.domain.models.module_subscriptions import ModuleSubscriptions
from app.v2_0.HRMS.domain.models.user_auth import UsersAuth
from app.v2_0.HRMS.domain.models.user_bank_details import UserBankDetails
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.models.user_documents import UserDocuments
from app.v2_0.HRMS.domain.models.user_finance import UserFinance
from app.v2_0.HRMS.domain.models.user_official_details import UserOfficialDetails
from app.v2_0.HRMS.domain.schemas.user_schemas import UpdateUser
from app.v2_0.infrastructure.database import get_db


def get_all_features(module_list: List[Modules]):
    available_features = []
    for module in module_list:
        for features in Features:
            if features.name.startswith(module.name):
                available_features.append(features)
    return available_features


def user_update_func(user: UpdateUser, user_id, company_id, branch_id, u_id, db=Depends(get_db)):
    """Updates a User"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if check is None:
            if u_id == "" or user_id is None:
                return add_emp(user, user_id, company_id, branch_id, u_id, db)

            else:
                """Update employee"""
                user_auth = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
                if user_auth is None:
                    db.rollback()
                    return ResponseDTO(404, "User not found!", {})
                else:
                    return update_user(user, user_id, company_id, branch_id, u_id, db)

        else:
            db.rollback()
            return check

    except Exception as e:
        db.rollback()
        return ResponseDTO(204, str(e), {})


def add_user_finances(user, user_id, new_employee, db):
    if user.financial is not None:
        finances = UserFinance(user_id=new_employee.user_id,
                               basic_salary=user.financial.finances.basic_salary,
                               BOA=user.financial.finances.BOA, bonus=user.financial.finances.bonus,
                               PF=user.financial.finances.PF,
                               performance_bonus=user.financial.finances.performance_bonus,
                               gratuity=user.financial.finances.gratuity,
                               deduction=user.financial.finances.deduction,
                               fixed_monthly_gross=user.financial.finances.fixed_monthly_gross,
                               total_annual_gross=user.financial.finances.total_annual_gross,
                               modified_by=user_id, modified_on=datetime.now())
    else:
        finances = UserFinance(user_id=new_employee.user_id)

    db.add(finances)
    db.flush()


def add_emp(user: UpdateUser, user_id, company_id, branch_id, u_id, db=Depends(get_db)):
    """Add employee"""

    if user.personal_info.user_email is None:
        db.rollback()
        return ResponseDTO(400, "Email is required!", {})
    else:
        """email validation"""
        email_exist = db.query(UsersAuth).filter(UsersAuth.user_email == user.personal_info.user_email).first()
        if email_exist:
            db.rollback()
            return ResponseDTO(204, "User with this email already exists", {})

        """contact Validation"""
        if user.personal_info.user_contact is not None:
            contact_exists = db.query(UserDetails).filter(
                UserDetails.user_contact == user.personal_info.user_contact).first()
            if contact_exists:
                db.rollback()
                return ResponseDTO(409, "User with this contact already exists!", contact_exists)

        accessible_modules = []
        accessible_features = []
        subscription = db.query(ModuleSubscriptions).filter(
            ModuleSubscriptions.company_id == company_id).filter(ModuleSubscriptions.branch_id == branch_id).first()
        new_employee = invite_new_user(user, user_id, company_id, branch_id, u_id, db)
        add_emp_in_ucb(user, company_id, branch_id, accessible_modules, accessible_features, new_employee, subscription,
                       db)

        """add user details"""
        add_user_details(user, user_id, new_employee, db)

    """add user official details"""
    add_user_official_details(user, user_id, new_employee, company_id, db)

    """add user documents"""
    if user.documents is not None:
        if user.documents.aadhar.aadhar_number is not None:
            aadhar = db.query(UserDocuments).filter(
                UserDocuments.aadhar_number == user.documents.aadhar.aadhar_number).first()
            if aadhar:
                db.rollback()
                return ResponseDTO(204, "Aadhar number already belongs to someone!", {})
        if user.documents.aadhar.pan_number is not None:
            aadhar = db.query(UserDocuments).filter(
                UserDocuments.pan_number == user.documents.aadhar.pan_number).first()
            if aadhar:
                db.rollback()
                return ResponseDTO(204, "pan number already belongs to someone!", {})
        if user.documents.passport.passport_num is not None:
            aadhar = db.query(UserDocuments).filter(
                UserDocuments.passport_num == user.documents.passport.passport_num).first()
            if aadhar:
                db.rollback()
                return ResponseDTO(204, "pan number already belongs to someone!", {})
    add_user_docs_data(user, user_id, new_employee, db)

    """ add  user finances"""
    add_user_finances(user, user_id, new_employee, db)

    """add user bank details"""
    if user.financial is not None:
        if user.financial.bank_details.account_number is not None:
            account_number = db.query(UserBankDetails).filter(
                UserBankDetails.account_number == user.financial.bank_details.account_number).first()
            if account_number:
                db.rollback()
                return ResponseDTO(204, "Account number already belongs to someone!", {})
        if user.financial.bank_details.ifsc_code is not None:
            ifsc_code = db.query(UserBankDetails).filter(
                UserBankDetails.ifsc_code == user.financial.bank_details.ifsc_code).first()
            if ifsc_code:
                db.rollback()
                return ResponseDTO(204, "IFSC code already belongs to someone!", {})

    add_user_bank_data(user, new_employee, db)
    db.commit()
    return ResponseDTO(200, "Employee added successfully!", {})


def add_emp_in_ucb(user: UpdateUser, company_id, branch_id, accessible_modules, accessible_features,
                   new_employee, subscription, db=Depends(get_db)):
    company = db.query(Companies).filter(Companies.company_id == company_id).first()
    approvers_list = [company.owner]
    if user.official.accessible_modules is None:
        accessible_modules = subscription.module_name
        accessible_features = get_all_features(accessible_modules)
    else:
        for module in user.official.accessible_modules:
            for modules in Modules:
                if modules.value == module.module_id:
                    accessible_modules.append(modules)
            for feature in module.accessible_features:
                for features in Features:
                    if features.value == feature.feature_id:
                        accessible_features.append(features)
    if user.official.approvers is None:
        approvers = [company.owner]
        approvers_list = list(approvers)
    elif len(user.official.approvers) != 0:
        approvers_set = set(user.official.approvers)
        if approvers_set.__contains__(company.owner) is False:
            approvers_set.add(company.owner)
        approvers_list = list(approvers_set)

    ucb_employee = UserCompanyBranch(user_id=new_employee.user_id, company_id=company_id,
                                     branch_id=branch_id,
                                     designations=user.official.designations, approvers=approvers_list,
                                     accessible_modules=accessible_modules,
                                     accessible_features=accessible_features)

    db.add(ucb_employee)
    db.flush()


def invite_new_user(user: UpdateUser, user_id, company_id, branch_id, u_id, db=Depends(get_db)):
    """Add new user"""
    inviter = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
    token = create_password_reset_code(user.personal_info.user_email, db)
    new_employee = UsersAuth(user_email=user.personal_info.user_email, invited_by=inviter.user_email,
                             change_password_token=token)
    db.add(new_employee)
    db.flush()
    return new_employee


def add_user_details(user, user_id, new_employee, db=Depends(get_db)):
    new_user = UserDetails(user_id=new_employee.user_id, first_name=user.personal_info.first_name,
                           last_name=user.personal_info.last_name,
                           middle_name=user.personal_info.middle_name,
                           user_contact=user.personal_info.user_contact,
                           alternate_contact=user.personal_info.alternate_contact,
                           user_image=user.personal_info.user_image,
                           user_birthdate=user.personal_info.user_birthdate,
                           age=user.personal_info.age, gender=user.personal_info.gender,
                           nationality=user.personal_info.nationality,
                           marital_status=user.personal_info.marital_status,
                           current_address=user.personal_info.current_address,
                           permanent_address=user.personal_info.permanent_address,
                           city=user.personal_info.city, state=user.personal_info.state,
                           pincode=user.personal_info.pincode,
                           activity_status=user.personal_info.active_status, modified_by=user_id,
                           modified_on=datetime.now())
    db.add(new_user)
    db.flush()
    return new_user


def add_user_official_details(user, user_id, new_employee, company_id, db):
    company = db.query(Companies).filter(Companies.company_id == company_id).first()
    if user.official is not None:

        official = UserOfficialDetails(user_id=new_employee.user_id, doj=user.official.doj,
                                       job_confirmation=user.official.job_confirmation,
                                       current_location=user.official.current_location,
                                       department_head=user.official.department_head if user.official.department_head else company.owner,
                                       reporting_manager=user.official.reporting_manager if user.official.department_head else company.owner,
                                       modified_by=user_id, modified_on=datetime.now())
    else:
        official = UserOfficialDetails(user_id=new_employee.user_id, department_head=company.owner,
                                       reporting_manager=company.owner, job_confirmation=False)
    db.add(official)
    db.flush()


def add_user_docs_data(user, user_id, new_employee, db):
    if user.documents is not None:
        docs = UserDocuments(user_id=new_employee.user_id,
                             aadhar_number=user.documents.aadhar.aadhar_number,
                             name_as_per_aadhar=user.documents.aadhar.name_as_per_aadhar,
                             pan_number=user.documents.aadhar.pan_number,
                             passport_num=user.documents.passport.passport_num,
                             passport_fname=user.documents.passport.passport_fname,
                             passport_lname=user.documents.passport.passport_lname,
                             expiry_date=user.documents.passport.expiry_date,
                             issue_date=user.documents.passport.issue_date,
                             mobile_number=user.documents.passport.mobile_number,
                             current_address=user.documents.passport.current_address,
                             permanent_address=user.documents.passport.permanent_address,
                             modified_by=user_id,
                             modified_on=datetime.now())
    else:
        docs = UserDocuments(user_id=new_employee.user_id)

    db.add(docs)
    db.flush()


def add_user_bank_data(user, new_employee, db):
    if user.financial is not None:
        bank = UserBankDetails(user_id=new_employee.user_id,
                               bank_name=user.financial.bank_details.bank_name,
                               account_number=user.financial.bank_details.account_number,
                               ifsc_code=user.financial.bank_details.ifsc_code,
                               branch_name=user.financial.bank_details.branch,
                               account_type=user.financial.bank_details.account_type,
                               country=user.financial.bank_details.country,
                               modified_on=datetime.now())
    else:
        bank = UserBankDetails(user_id=new_employee.user_id)

    db.add(bank)
    db.flush()


def update_user(user: UpdateUser, user_id, company_id, branch_id, u_id, db=Depends(get_db)):
    accessible_modules = []
    accessible_features = []
    approvers_list = []
    company = db.query(Companies).filter(Companies.company_id == company_id).first()
    subscription = db.query(ModuleSubscriptions).filter(
        ModuleSubscriptions.company_id == company_id).first()
    if user.personal_info.user_email is not None:
        email_exist = db.query(UsersAuth).filter(
            UsersAuth.user_email == user.personal_info.user_email).filter(UsersAuth.user_id != u_id).first()
        if email_exist:
            db.rollback()
            return ResponseDTO(204, "User with this email already exists", {})

    if user.personal_info.user_contact is not None:
        contact_exists = db.query(UserDetails).filter(
            UserDetails.user_contact == user.personal_info.user_contact).filter(UserDetails.user_id != u_id).first()
        if contact_exists:
            db.rollback()
            return ResponseDTO(409, "User with this contact already exists!", {})
    if user.official.accessible_modules is None:
        accessible_modules = subscription.module_name
        accessible_features = get_all_features(accessible_modules)
    else:
        for module in user.official.accessible_modules:
            for modules in Modules:
                if modules.value == module.module_id:
                    accessible_modules.append(modules)
            for feature in module.accessible_features:
                for features in Features:
                    if features.value == feature.feature_id:
                        accessible_features.append(features)
    if user.official.approvers is None:
        approvers = [company.owner]
        approvers_list = list(approvers)
    elif len(user.official.approvers) != 0:
        approvers_set = set(user.official.approvers)
        if approvers_set.__contains__(company.owner) is False:
            approvers_set.add(company.owner)
        approvers_list = list(approvers_set)

    """update user_auth"""
    db.query(UsersAuth).filter(UsersAuth.user_id == u_id).update(
        {"user_email": user.personal_info.user_email, "modified_on": datetime.now(),
         "modified_by": user_id})

    """update ucb"""
    db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == u_id).filter(
        UserCompanyBranch.company_id == company_id).filter(
        UserCompanyBranch.branch_id == branch_id).update(
        {"designations": user.official.designations, "approvers": approvers_list,
         "accessible_modules": accessible_modules,
         "accessible_features": accessible_features, "modified_on": datetime.now(),
         "modified_by": user_id})

    """update personal_info_update"""

    db.query(UserDetails).filter(UserDetails.user_id == u_id).update(
        {"first_name": user.personal_info.first_name, "last_name": user.personal_info.last_name,
         "middle_name": user.personal_info.middle_name,
         "user_contact": user.personal_info.user_contact,
         "alternate_contact": user.personal_info.alternate_contact,
         "user_image": user.personal_info.user_image,
         "user_birthdate": user.personal_info.user_birthdate,
         "age": user.personal_info.age, "gender": user.personal_info.gender,
         "nationality": user.personal_info.nationality,
         "marital_status": user.personal_info.marital_status,
         "current_address": user.personal_info.current_address,
         "permanent_address": user.personal_info.permanent_address, "city": user.personal_info.city,
         "state": user.personal_info.state,
         "pincode": user.personal_info.pincode, "modified_on": datetime.now(), "modified_by": user_id})

    """update user_official_details"""
    db.query(UserOfficialDetails).filter(
        UserOfficialDetails.user_id == u_id).update(
        {"doj": user.official.doj, "job_confirmation": user.official.job_confirmation,
         "current_location": user.official.current_location,
         "department_head": user.official.department_head if user.official.department_head else company.owner,
         "reporting_manager": user.official.reporting_manager if user.official.department_head else company.owner,
         "modified_on": datetime.now(), "modified_by": user_id})

    """update user_documents"""
    if user.documents is not None:
        if user.documents.aadhar.aadhar_number is not None:
            aadhar = db.query(UserDocuments).filter(
                UserDocuments.aadhar_number == user.documents.aadhar.aadhar_number).filter(
                UserDocuments.user_id != u_id).first()
            if aadhar:
                db.rollback()
                return ResponseDTO(204, "Aadhar number already belongs to someone!", {})
        if user.documents.aadhar.pan_number is not None:
            pan_num = db.query(UserDocuments).filter(
                UserDocuments.pan_number == user.documents.aadhar.pan_number).filter(
                UserDocuments.user_id != u_id).first()
            if pan_num:
                db.rollback()
                return ResponseDTO(204, "pan number already belongs to someone!", {})
        if user.documents.passport.passport_num is not None:
            passport = db.query(UserDocuments).filter(
                UserDocuments.passport_num == user.documents.passport.passport_num).filter(
                UserDocuments.user_id != u_id).first()
            if passport:
                db.rollback()
                return ResponseDTO(204, "Passport number already belongs to someone!", {})
    db.query(UserDocuments).filter(UserDocuments.user_id == u_id).update(
        {"aadhar_number": user.documents.aadhar.aadhar_number,
         "name_as_per_aadhar": user.documents.aadhar.name_as_per_aadhar,
         "pan_number": user.documents.aadhar.pan_number,
         "passport_num": user.documents.passport.passport_num,
         "passport_fname": user.documents.passport.passport_fname,
         "passport_lname": user.documents.passport.passport_lname,
         "expiry_date": user.documents.passport.expiry_date,
         "issue_date": user.documents.passport.issue_date,
         "mobile_number": user.documents.passport.mobile_number,
         "current_address": user.documents.passport.current_address,
         "permanent_address": user.documents.passport.permanent_address, "modified_on": datetime.now(),
         "modified_by": user_id})

    """user finances update"""
    db.query(UserFinance).filter(UserFinance.user_id == u_id).update(
        {"basic_salary": user.financial.finances.basic_salary,
         "BOA": user.financial.finances.BOA,
         "bonus": user.financial.finances.bonus,
         "PF": user.financial.finances.PF,
         "performance_bonus": user.financial.finances.performance_bonus,
         "gratuity": user.financial.finances.gratuity,
         "deduction": user.financial.finances.deduction,
         "fixed_monthly_gross": user.financial.finances.fixed_monthly_gross,
         "total_annual_gross": user.financial.finances.total_annual_gross,
         "modified_on": datetime.now(),
         "modified_by": user_id})

    """user bank details update"""
    if user.financial.bank_details.account_number is not None:
        account_number = db.query(UserBankDetails).filter(
            UserBankDetails.account_number == user.financial.bank_details.account_number).filter(
            UserBankDetails.user_id != u_id).first()
        if account_number:
            db.rollback()
            return ResponseDTO(204, "Account number already belongs to someone!", {})
    if user.financial.bank_details.ifsc_code is not None:
        ifsc_code = db.query(UserBankDetails).filter(
            UserBankDetails.ifsc_code == user.financial.bank_details.ifsc_code).filter(
            UserBankDetails.user_id != u_id).first()
        if ifsc_code:
            db.rollback()
            return ResponseDTO(204, "IFSC code already belongs to someone!", {})
    db.query(UserBankDetails).filter(UserBankDetails.user_id == u_id).update(
        {"bank_name": user.financial.bank_details.bank_name,
         "account_number": user.financial.bank_details.account_number,
         "ifsc_code": user.financial.bank_details.ifsc_code,
         "branch_name": user.financial.bank_details.branch,
         "account_type": user.financial.bank_details.account_type,
         "country": user.financial.bank_details.country,
         "modified_on": datetime.now()})

    db.commit()
    return ResponseDTO(200, "User updated successfully!", {})

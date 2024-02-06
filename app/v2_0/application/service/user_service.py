"""Service layer for Users"""
from datetime import datetime

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.password_handler.pwd_encrypter_decrypter import hash_pwd
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.application.service.ucb_service import add_owner_to_ucb, add_employee_to_ucb
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.domain.models.branch_settings import BranchSettings
from app.v2_0.domain.models.companies import Companies
from app.v2_0.domain.models.leaves import Leaves
from app.v2_0.domain.models.user_auth import UsersAuth
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.models.user_details import UserDetails
from app.v2_0.domain.models.user_documents import UserDocuments
from app.v2_0.domain.models.user_finance import UserFinance
from app.v2_0.domain.schemas.employee_schemas import InviteEmployee
from app.v2_0.domain.schemas.user_schemas import GetUser


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
        add_owner_to_ucb(new_user, db)

        return ResponseDTO(200, "User created successfully",
                           {"user_id": new_user.user_id, "name": user.first_name + " " + user.last_name, "company": []})

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def get_designations(user_id, db):
    user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()
    return user.designations


def fetch_by_id(u_id, company_id, branch_id, db):
    """Fetches a user by his id"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is not None:
            return check

        else:
            user = db.query(UserDetails).filter(UserDetails.user_id == u_id).first()

            if user is None:
                return ResponseDTO(404, "User not found!", {})

            user_auth = db.query(UsersAuth).filter(UsersAuth.user_id == u_id).first()
            user_doc = db.query(UserDocuments).filter(UserDocuments.user_id == u_id).first()
            user_finances = db.query(UserFinance).filter(UserFinance.user_id == u_id).first()

            user.__dict__["user_email"] = user_auth.user_email
            user.__dict__["designations"] = get_designations(u_id, db)

            user_details = user.__dict__.copy()
            user_details.update(user_doc.__dict__ if user_doc else {})
            user_details.update(user_finances.__dict__ if user_finances else {})
            return ResponseDTO(200, "User fetched!", GetUser(**user_details))

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

    aadhar_query = db.query(UserDocuments).filter(UserDocuments.aadhar_number == new_docs_data["aadhar_number"]).filter(
        UserDocuments.user_id != u_id).first()
    pan_query = db.query(UserDocuments).filter(UserDocuments.pan_number == new_docs_data["pan_number"]).filter(
        UserDocuments.user_id != u_id).first()
    passport_query = db.query(UserDocuments).filter(UserDocuments.passport_num == new_docs_data["passport_num"]).filter(
        UserDocuments.user_id != u_id).first()

    resp = validate_docs(aadhar_query, pan_query, passport_query)
    if resp is not None:
        return resp

    docs_query = db.query(UserDocuments).filter(UserDocuments.user_id == u_id)
    docs_query.update(new_docs_data)

    return None


def update_user_finance(finance_data, u_id, user_id, db):
    finance_data.__dict__["modified_on"] = datetime.now()
    finance_data.__dict__["modified_by"] = user_id

    finance_query = db.query(UserFinance).filter(UserFinance.user_id == u_id)
    finance_query.update(finance_data.__dict__)


def store_personal_info(personal_data, user_id, branch_id, db):
    user_contact = db.query(UserDetails).filter(
        UserDetails.user_contact == personal_data.__dict__["user_contact"]).first()
    if user_contact is not None:
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
    aadhar_query = db.query(UserDocuments).filter(UserDocuments.aadhar_number == new_docs_data["aadhar_number"]).first()
    pan_query = db.query(UserDocuments).filter(UserDocuments.pan_number == new_docs_data["pan_number"]).first()
    passport_query = db.query(UserDocuments).filter(UserDocuments.passport_num == new_docs_data["passport_num"]).first()
    resp = validate_docs(aadhar_query, pan_query, passport_query)
    if resp is not None:
        return resp
    docs = UserDocuments(**new_docs_data)
    db.add(docs)

    return None


def store_user_finance(finance_data, user_id, db):
    data = UserFinance(salary=finance_data.salary, user_id=user_id)
    db.add(data)


def add_employee_manually(user, user_id, company_id, branch_id, db):
    """Adds an employee with his details to the DB"""
    email = user.__dict__["personal_info"].user_email
    user_in_user_auth = db.query(UsersAuth).filter(UsersAuth.user_email == email).first()

    if user_in_user_auth is None:
        inviter = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        new_employee = UsersAuth(user_email=email,
                                 invited_by=inviter.user_email)
        db.add(new_employee)
        db.flush()

        ucb_emp = InviteEmployee
        ucb_emp.approvers = user.approvers
        ucb_emp.designations = user.designations
        ucb_emp.accessible_modules = user.accessible_modules
        ucb_emp.accessible_features = user.accessible_features
        add_employee_to_ucb(ucb_emp, new_employee, company_id, branch_id, db)

        info_resp = store_personal_info(user.personal_info, new_employee.user_id, branch_id, db)
        if info_resp is not None:
            return info_resp

        docs_resp = store_user_documents(user.documents, new_employee.user_id, db)
        if docs_resp is not None:
            return docs_resp

        store_user_finance(user.financial, new_employee.user_id, db)

        create_password_reset_code(email, db)

        db.commit()
    else:
        user_exists = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_in_user_auth.user_id).filter(
            UserCompanyBranch.branch_id == branch_id).first()

        if user_in_user_auth and user_exists:
            return ResponseDTO(409, "User with this email already exists in this branch!", user_exists)

        elif user_in_user_auth and not user_exists:
            add_employee_to_ucb(user, user_in_user_auth, company_id, branch_id, db)
            db.commit()

    return None


def modify_user(user, user_id, company_id, branch_id, u_id, db):
    """Updates a User"""
    """user_id is the person who will be updating the person with u_id as the user_id"""

    # try:

    check = check_if_company_and_branch_exist(company_id, branch_id, db)

    if check is not None:
        return check

    else:
        if u_id == "":

            response = add_employee_manually(user, user_id, company_id, branch_id, db)

            if response is None:
                return ResponseDTO(200, "User added successfully", {})
            else:
                return response
        else:
            user_query = db.query(UserDetails).filter(UserDetails.user_id == int(u_id))
            user_exists = user_query.first()

            contact_exists = db.query(UserDetails).filter(
                UserDetails.user_contact == user.personal_info.user_contact).filter(
                UserDetails.user_id != u_id).first()

            if not user_exists:
                return ResponseDTO(404, "User not found!", {})
            if contact_exists:
                return ResponseDTO(409, "User with this contact already exists!", contact_exists)

            update_personal_info(user.personal_info, user_query, user_id)

            docs_resp = update_user_documents(user.documents, u_id, user_id, db)
            if docs_resp is not None:
                return docs_resp

            update_user_finance(user.financial, u_id, user_id, db)
            db.commit()

            return ResponseDTO(200, "User updated successfully", {})


# except Exception as exc:
#     db.rollback()
#     return ResponseDTO(204, str(exc), {})


def update_leave_approvers(approvers_list, user_id, db):
    leave_query = db.query(Leaves).filter(Leaves.user_id == user_id)
    leave_query.update({"approvers": approvers_list})
    db.commit()


def update_approver(approver, user_id, company_id, branch_id, db):
    """Adds an approver to the list of approvers of a user"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, db)
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

            if not flag or len(approvers_list) == 0:
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

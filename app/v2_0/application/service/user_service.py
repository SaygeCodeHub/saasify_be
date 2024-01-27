"""Service layer for Users"""
from datetime import datetime

from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.application.password_handler.pwd_encrypter_decrypter import hash_pwd
from app.v2_0.application.password_handler.reset_password import create_password_reset_code
from app.v2_0.application.utility.app_utility import add_employee_to_ucb
from app.v2_0.domain import models
from app.v2_0.domain.schema import GetUser, InviteEmployee


def add_user_details(user, user_id, db):
    """Adds user details in the db"""
    try:
        user_details = models.UserDetails(user_id=user_id, first_name=user.first_name, last_name=user.last_name,
                                          activity_status=user.activity_status)
        db.add(user_details)
        db.commit()
        db.refresh(user_details)
        user_docs = models.UserDocuments(user_id=user_id)
        db.add(user_docs)
        db.commit()
        user_finance = models.UserFinance(user_id=user_id)
        db.add(user_finance)
        db.commit()
    except Exception as exc:
        return ExceptionDTO("add_user_details", exc)


def add_to_ucb(new_user, db):
    """Adds the data mapped to a user into db"""
    try:
        approvers_list = [new_user.user_id]
        ucb = models.UserCompanyBranch(user_id=new_user.user_id, approvers=approvers_list)
        db.add(ucb)
        db.commit()
    except Exception as exc:
        return ExceptionDTO("add_to_ucb", exc)


def add_user(user, db):
    """Adds a user into the database"""
    # try:
    user_email_exists = db.query(models.UsersAuth).filter(
        models.UsersAuth.user_email == user.user_email).first()

    if user_email_exists:
        return ResponseDTO(403, "User with this email already exists", {})
    hashed_pwd = hash_pwd(user.password)
    user.password = hashed_pwd
    new_user = models.UsersAuth(user_email=user.user_email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    add_user_details(user, new_user.user_id, db)
    add_to_ucb(new_user, db)

    return ResponseDTO(200, "User created successfully",
                       {"user_id": new_user.user_id, "name": user.first_name + " " + user.last_name, "company": []})


# except Exception as exc:
#     return ExceptionDTO("add_user", exc)


def get_roles(user_id, db):
    user = db.query(models.UserCompanyBranch).filter(models.UserCompanyBranch.user_id == user_id).first()
    return user.roles


def fetch_by_id(u_id, company_id, branch_id, db):
    """Fetches a user by his id"""
    try:
        company = db.query(models.Companies).filter(models.Companies.company_id == company_id).first()
        if company is None:
            return ResponseDTO(404, "Company not found!", {})

        branch = db.query(models.Branches).filter(models.Branches.branch_id == branch_id).first()
        if branch is None:
            return ResponseDTO(404, "Branch not found!", {})

        user = db.query(models.UserDetails).filter(models.UserDetails.user_id == u_id).first()

        if user is None:
            return ResponseDTO(404, "User not found!", {})

        user_auth = db.query(models.UsersAuth).filter(models.UsersAuth.user_id == u_id).first()
        user.__dict__["user_email"] = user_auth.user_email
        user.__dict__["roles"] = get_roles(u_id, db)
        result = GetUser(**user.__dict__)
        return ResponseDTO(200, "User fetched!", result)

    except Exception as exc:
        return ExceptionDTO("fetch_by_id", exc)


def update_personal_info(personal_data, user_query, user_id, db):
    # Deleting the 'user_email' field from personal_data dictionary because the UserDetails table does not contain email column
    del personal_data.__dict__["user_email"]

    personal_data.__dict__["modified_on"] = datetime.now()
    personal_data.__dict__["modified_by"] = user_id
    user_query.update(personal_data.__dict__)
    db.commit()


def update_user_documents(docs_data, u_id, user_id, db):
    # Unpacking the 2 dictionaries - aadhar and passport and storing them in a new dictionary
    new_docs_data = {**docs_data.__dict__["aadhar"].__dict__, **docs_data.__dict__["passport"].__dict__,
                     "modified_on": datetime.now(), "modified_by": user_id}
    docs_query = db.query(models.UserDocuments).filter(models.UserDocuments.user_id == u_id)
    docs_query.update(new_docs_data)
    db.commit()


def update_user_finance(finance_data, u_id, user_id, db):
    finance_data.__dict__["modified_on"] = datetime.now()
    finance_data.__dict__["modified_by"] = user_id

    finance_query = db.query(models.UserFinance).filter(models.UserFinance.user_id == u_id)
    finance_query.update(finance_data.__dict__)
    db.commit()


def store_personal_info(personal_data, user_id, db):
    new_employee = models.UserDetails(user_id=user_id, first_name=personal_data.__dict__["first_name"],
                                      last_name=personal_data.__dict__["last_name"],
                                      activity_status=personal_data.__dict__["activity_status"])
    db.add(new_employee)
    db.commit()


def store_user_documents(docs_data, user_id, db):
    new_docs_data = {**docs_data.__dict__["aadhar"].__dict__, **docs_data.__dict__["passport"].__dict__,
                     "user_id": user_id}
    docs = models.UserDocuments(**new_docs_data)
    db.add(docs)
    db.commit()


def store_user_finance(finance_data, user_id, db):
    data = models.UserFinance(salary=finance_data.salary, user_id=user_id)
    db.add(data)
    db.commit()


def add_employee_manually(user, user_id, company_id, branch_id, db):
    email = user.__dict__["personal_info"].user_email
    inviter = db.query(models.UsersAuth).filter(models.UsersAuth.user_id == user_id).first()
    new_employee = models.UsersAuth(user_email=email,
                                    invited_by=inviter.user_email)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    ucb_emp = InviteEmployee
    ucb_emp.approvers = user.approvers
    ucb_emp.roles = user.roles
    add_employee_to_ucb(ucb_emp, new_employee, company_id, branch_id, db)
    create_password_reset_code(email, db)

    store_personal_info(user.__dict__["personal_info"], new_employee.user_id, db)
    store_user_documents(user.__dict__["documents"], new_employee.user_id, db)
    store_user_finance(user.__dict__["financial"], new_employee.user_id, db)


def modify_user(user, user_id, company_id, branch_id, u_id, db):
    """Updates a User"""
    """user_id is the person who will be updating the person with u_id as the user_id"""
    # try:
    company = db.query(models.Companies).filter(models.Companies.company_id == company_id).first()
    if company is None:
        return ResponseDTO(404, "Company not found!", {})

    branch = db.query(models.Branches).filter(models.Branches.branch_id == branch_id).first()
    if branch is None:
        return ResponseDTO(404, "Branch not found!", {})

    if u_id == "":

        add_employee_manually(user, user_id, company_id, branch_id, db)

        return ResponseDTO(200, "User added successfully", {})

    else:
        user_query = db.query(models.UserDetails).filter(models.UserDetails.user_id == int(u_id))
        user_exists = user_query.first()
        # contact_exists = db.query(models.UserDetails).filter(
        #     models.UserDetails.user_contact == user.__dict__["personal_info"].user_contact).first()

        if not user_exists:
            return ResponseDTO(404, "User not found!", {})
        # if contact_exists:
        #     return ResponseDTO(403, "User with this contact already exists!", {})

        update_personal_info(user.__dict__["personal_info"], user_query, user_id, db)
        update_user_documents(user.__dict__["documents"], u_id, user_id, db)
        update_user_finance(user.__dict__["financial"], u_id, user_id, db)
        return ResponseDTO(200, "User updated successfully", {})


# except Exception as exc:
#     return ExceptionDTO("modify_user", exc)


def update_leave_approvers(approvers_list, user_id, db):
    leave_query = db.query(models.Leaves).filter(models.Leaves.user_id == user_id)
    leave_query.update({"approvers": approvers_list})
    db.commit()


def update_approver(approver, user_id, company_id, branch_id, db):
    """Adds an approver to the list of approvers of a user"""
    try:
        company_exists = db.query(models.Companies).filter(models.Companies.company_id == company_id).first()
        if company_exists is None:
            return ResponseDTO(404, "Company does not exist!", {})

        branch_exists = db.query(models.Branches).filter(models.Branches.branch_id == branch_id).first()
        if branch_exists is None:
            return ResponseDTO(404, "Branch does not exist!", {})

        flag = True
        user_query = db.query(models.UserCompanyBranch).filter(models.UserCompanyBranch.user_id == user_id)
        user = user_query.first()

        if user is None:
            return ResponseDTO(404, "User not found", {})

        company = db.query(models.Companies).filter(models.Companies.company_id == user.company_id).first()

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

    except Exception as exc:
        return ExceptionDTO("update_approver", exc)

"""Service layer for Users"""
from datetime import datetime

from sqlalchemy import select

from app.v2_0.application.password_handler.pwd_encrypter_decrypter import hash_pwd
from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.domain import models


def add_user_details(user, user_id, db):
    """Adds user details in the db"""
    try:
        user_details = models.UserDetails(user_id=user_id, first_name=user.first_name, last_name=user.last_name,
                                          modified_by=user_id, medical_leaves=user.medical_leaves,
                                          casual_leaves=user.casual_leaves, activity_status=user.activity_status,
                                          modified_on=datetime.now())
        db.add(user_details)
        db.commit()
        db.refresh(user_details)
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
    try:
        user_email_exists = db.query(models.UsersAuth).filter(
            models.UsersAuth.user_email == user.user_email).first()

        if user_email_exists:
            return ResponseDTO(403, "User with this email already exists", {})
        hashed_pwd = hash_pwd(user.password)
        user.password = hashed_pwd
        new_user = models.UsersAuth(user_email=user.user_email, password=user.password, modified_by=-1)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        set_modified_by(new_user, db)
        add_user_details(user, new_user.user_id, db)
        add_to_ucb(new_user, db)

        return ResponseDTO(200, "User created successfully",
                           {"user_id": new_user.user_id, "name": user.first_name + " " + user.last_name, "company": []})
    except Exception as exc:
        return ExceptionDTO("add_user", exc)


def set_modified_by(new_user, db):
    """Sets the 'modified by' column of a User"""
    try:
        db.query(models.UsersAuth).filter(models.UsersAuth.user_id == new_user.user_id).update(
            {"modified_by": new_user.user_id})
        db.commit()
    except Exception as exc:
        return ExceptionDTO("set_modified_by", exc)


def fetch_by_id(user_id, db):
    """Fetches a user by his id"""
    try:
        user = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id).first()
        user_auth = db.query(models.UsersAuth).filter(models.UsersAuth.user_id == user_id).first()
        user.__dict__["user_email"] = user_auth.user_email
        return user
    except Exception as exc:
        return ExceptionDTO("fetch_by_id", exc)


def modify_user(user, user_id, db):
    """Updates a User"""
    try:
        user_query = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id)
        user_exists = user_query.first()
        contact_exists = db.query(models.UserDetails).filter(
            models.UserDetails.user_contact == user.user_contact).first()

        if not user_exists:
            return ResponseDTO(404, "User not found!", {})
        if contact_exists:
            return ResponseDTO(403, "User with this contact already exists!", {})

        user.modified_on = datetime.now()
        user.modified_by = user_exists.user_id
        user_query.update(user.__dict__)
        db.commit()

        return ResponseDTO(200, "User updated successfully", {})
    except Exception as exc:
        return ExceptionDTO("modify_user", exc)


def update_approver(approver, user_id, company_id, branch_id, db):
    """Adds an approver to the list of approvers of a user"""
    try:
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

        return ResponseDTO(200, "Approvers added!", {})

    except Exception as exc:
        return ExceptionDTO("add_new_approver", exc)

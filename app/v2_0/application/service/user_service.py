"""Service layer for Users"""
from datetime import datetime

from sqlalchemy import select

from app.v2_0.application.password_handler.pwd_encrypter_decrypter import hash_pwd
from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.domain import models


def add_user_details(user, user_id, db):
    user_details = models.UserDetails(user_id=user_id, first_name=user.first_name, last_name=user.last_name,
                                      modified_by=user_id, medical_leaves=user.medical_leaves,
                                      casual_leaves=user.casual_leaves, activity_status=user.activity_status,
                                      modified_on=datetime.now())
    db.add(user_details)
    db.commit()
    db.refresh(user_details)


def add_to_ucb(new_user, db):
    approvers_list = [new_user.user_id]
    ucb = models.UserCompanyBranch(user_id=new_user.user_id,approvers=approvers_list)
    db.add(ucb)
    db.commit()


def add_user(user, db):
    """Adds a user into the database"""
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

    return ResponseDTO(200, "User created successfully", {"user_id": new_user.user_id, "company": []})


def set_modified_by(new_user, db):
    """Sets the 'modified by' column of a User"""
    db.query(models.UsersAuth).filter(models.UsersAuth.user_id == new_user.user_id).update(
        {"modified_by": new_user.user_id})
    db.commit()


def fetch_by_id(user_id, db):
    user = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id).first()
    user_auth = db.query(models.UsersAuth).filter(models.UsersAuth.user_id == user_id).first()
    user.__dict__["user_email"] = user_auth.user_email
    return user


def modify_user(user, user_id, db):
    """Updates a User"""
    user_query = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id)
    user_exists = user_query.first()
    contact_exists = db.query(models.UserDetails).filter(models.UserDetails.user_contact == user.user_contact).first()

    if not user_exists:
        return ResponseDTO(404, "User not found!", {})
    if contact_exists:
        return ResponseDTO(403, "User with this contact already exists!", {})

    user.modified_on = datetime.now()
    user.modified_by = user_exists.user_id
    user_query.update(user.__dict__)
    db.commit()

    return ResponseDTO(200, "User updated successfully", {})

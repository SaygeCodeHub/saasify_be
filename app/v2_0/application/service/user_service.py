"""Service layer for Users"""
from datetime import datetime

from app.v2_0.application.password_handler.pwd_encrypter_decrypter import hash_pwd
from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.domain import models


def add_user(user, db):
    """Adds a user into the database"""
    user_email_exists = db.query(models.Users).filter(
        models.Users.user_email == user.user_email).first()
    user_contact_exists = db.query(models.Users).filter(
        models.Users.user_contact == user.user_contact).first()

    if user_email_exists:
        return ResponseDTO(403, "User with this email already exists", {})
    elif user_contact_exists is None:
        pass
    hashed_pwd = hash_pwd(user.password)
    user.password = hashed_pwd
    new_user = models.Users(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    set_modified_by(new_user, db)
    ucb = models.UserCompanyBranch(user_id=new_user.user_id)
    db.add(ucb)
    db.commit()
    return ResponseDTO(200, "User created successfully", {"user_id":new_user.user_id,"company":[]})


def set_modified_by(new_user, db):
    """Sets the 'modified by' column of a User"""
    db.query(models.Users).filter(models.Users.user_id == new_user.user_id).update(
        {"modified_by": new_user.user_id})
    db.commit()


def modify_user(user, user_id, db):
    """Updates a User"""
    user_query = db.query(models.Users).filter(models.Users.user_id == user_id)
    user_exists = user_query.first()

    if not user_exists:
        return ResponseDTO(404, "User not found!", {})

    user.modified_on = datetime.now()
    user.modified_by = user_exists.user_id
    user_query.update(user.__dict__)
    db.commit()

    return ResponseDTO(200, "User updated successfully", {})

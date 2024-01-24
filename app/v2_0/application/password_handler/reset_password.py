"""Contains methods to reset password. Flow starts from the bottom most function of the file"""
import string
import random
import smtplib

from app.v2_0.application.password_handler.pwd_encrypter_decrypter import hash_pwd
from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.domain import models

"""-------------------------------Password update code starts below this line-----------------------------"""


def check_token(token, user_email, db):
    """Verifies the reset token stored in DB, against the token entered by an individual"""
    try:
        user = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == user_email).first()
        if user.change_password_token != token:
            return ResponseDTO(204, "Reset token doesn't match", {})

        return ResponseDTO(200, "Reset token matched!", {})
    except Exception as exc:
        return ExceptionDTO("check_token", exc)


def change_password(obj, db):
    """Updates the password and makes the change_password_token null in db"""
    try:
        user_query = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == obj.model_dump()["email"])
        user = user_query.first()

        if not user:
            return ResponseDTO(404, "User not found!", {})

        hashed_pwd = hash_pwd(obj.model_dump()["password"])
        user_query.update({"change_password_token": None, "password": hashed_pwd})
        db.commit()

        return ResponseDTO(200, "Password updated successfully!", {})
    except Exception as exc:
        return ExceptionDTO("change_password", exc)


"""-------------------------------Code below this line sends the change_password_token to an individual-----------------------------"""


def create_smtp_session(fetched_email, msg):
    """Creates a smtp session and sends an email. The exception handling is done by the library itself"""
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()

        # Authentication
        s.login("jayraj.manoj@gmail.com", "odxfrxoyfcgzwsks")

        s.sendmail("jayraj.manoj@gmail.com", fetched_email, msg)

        s.quit()
    except Exception as exc:
        return ExceptionDTO("create_smtp_session", exc)


def temporarily_add_token(reset_code, fetched_email, db):
    """Temporarily stores the reset code in DB"""
    try:
        user_query = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == fetched_email)

        user_query.update({"change_password_token": reset_code})
        db.commit()
        create_smtp_session(fetched_email, reset_code)
    except Exception as exc:
        return ExceptionDTO("temporarily_add_token", exc)


def create_password_reset_code(fetched_email, db):
    """Creates a 6 digit reset code"""
    try:
        code_length = 6
        reset_code = ''.join(random.choices(string.ascii_uppercase +
                                            string.digits, k=code_length))

        temporarily_add_token(reset_code, fetched_email, db)
        return reset_code
    except Exception as exc:
        return ExceptionDTO("create_password_reset_code", exc)


def initiate_pwd_reset(user_email, db):
    """Fetches the user who has requested for password reset and calls a method to create a smtp session"""
    try:
        fetched_user = db.query(models.UsersAuth).filter(models.UsersAuth.user_email == user_email).first()
        if fetched_user:
            fetched_email = fetched_user.user_email
            create_password_reset_code(fetched_email, db)
        else:
            return ResponseDTO(404, "User not found", {})
        return ResponseDTO(200, "Email sent successfully", {})

    except Exception as exc:
        return ExceptionDTO("initiate_pwd_reset", exc)

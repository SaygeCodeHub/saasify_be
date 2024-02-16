"""Contains methods to reset password. Flow starts from the bottom most function of the file"""
import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.v2_0.HRMS.application.password_handler.pwd_encrypter_decrypter import hash_pwd
from app.v2_0.HRMS.domain.models.user_auth import UsersAuth
from app.v2_0.dto.dto_classes import ResponseDTO

"""-------------------------------Update password code starts below this line-----------------------------"""


def check_token(obj, db):
    """Verifies the reset token stored in DB, against the token entered by an individual"""
    try:
        user = db.query(UsersAuth).filter(UsersAuth.user_email == obj.email).first()
        if user is None:
            return ResponseDTO(404, "User not found!", {})
        else:
            if user.change_password_token != obj.token:
                return ResponseDTO(204, "Reset token doesn't match", {})
            else:
                return change_password(obj, db)
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def change_password(obj, db):
    """Updates the password and makes the change_password_token null in db"""
    user_query = db.query(UsersAuth).filter(UsersAuth.user_email == obj.model_dump()["email"])
    user = user_query.first()

    if user is None:
        return ResponseDTO(404, "User with this email does not exist!", {})

    if user.change_password_token != obj.model_dump()["token"]:
        return ResponseDTO(204, "Reset token doesn't match", {})

    hashed_pwd = hash_pwd(obj.model_dump()["password"])
    user_query.update({"change_password_token": None, "password": hashed_pwd})
    db.commit()

    return ResponseDTO(200, "Password updated successfully!", {})


"""-------------------------------Code below this line sends the change_password_token to an individual-----------------------------"""


def create_smtp_session(fetched_email, reset_code):
    """Creates a smtp session and sends an email. The exception handling is done by the library itself"""
    tada = '\U0001F389'
    rocket = '\U0001F680'
    raised_hands = '\U0001F64C'
    # confetti_ball = '\U0001F38A'
    heart = '\u2764'
    subject = f"Welcome to Saasify! {rocket}"
    body = f"Hey!\nWelcome to SaaSify!  {tada} You are one step away to start your journey {raised_hands}\n\nHere is your One Time Password (OTP) -{reset_code}\n\nHave questions or need assistance?\nReach out anytime at saasify@sayge.in\n\nWe're here to ensure your experience is nothing short of exceptional.\n\nThank you for joining SaaSify {heart}\n\nBest regards,\nSaasify Support Team"
    msg = MIMEMultipart()
    msg['From'] = "jayraj.manoj@gmail.com"
    msg['To'] = fetched_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()

    # Authentication
    s.login("jayraj.manoj@gmail.com", "odxfrxoyfcgzwsks")

    s.sendmail("jayraj.manoj@gmail.com", fetched_email, msg.as_string())

    s.quit()


def temporarily_add_token(reset_code, fetched_email, db):
    """Temporarily stores the reset code in DB"""

    user_query = db.query(UsersAuth).filter(UsersAuth.user_email == fetched_email)

    user_query.update({"change_password_token": reset_code})

    create_smtp_session(fetched_email, reset_code)


def create_password_reset_code(fetched_email, db):
    """Creates a 6 digit reset code"""
    code_length = 6
    reset_code = ''.join(random.choices(string.ascii_uppercase +
                                        string.digits, k=code_length))

    temporarily_add_token(reset_code, fetched_email, db)
    return reset_code


def initiate_pwd_reset(email, db):
    """Fetches the user who has requested for password reset and calls a method to create a smtp session"""
    try:
        fetched_user = db.query(UsersAuth).filter(UsersAuth.user_email == email).first()
        if fetched_user:
            fetched_email = fetched_user.user_email
            create_password_reset_code(fetched_email, db)
            db.commit()
        else:
            return ResponseDTO(404, "User not found", {})
        return ResponseDTO(200, "Email sent successfully", {})

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

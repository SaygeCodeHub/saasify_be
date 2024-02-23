from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import Depends

from app.v2_0.HRMS.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.attendance import Attendance
from app.v2_0.HRMS.domain.models.leaves import Leaves
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.dto.dto_classes import ResponseDTO
from app.v2_0.enums import LeaveStatus, LeaveType
from app.v2_0.infrastructure.database import get_db


def fetch_attendance_today(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.company_id == company_id).filter(
        Attendance.branch_id == branch_id).filter(Attendance.user_id == user_id).filter(
        Attendance.date == date.today()).first()

    return attendance


def user_attendance_list(company_id: int, branch_id: int, user_id: int, db=Depends(get_db), u_id: Optional[str] = None):
    attendance = (db.query(Attendance).filter(Attendance.user_id == (u_id if u_id else user_id)).filter(
        Attendance.company_id == company_id).filter(Attendance.branch_id == branch_id).all())

    return attendance


def calculate_working_hours(checkIn, checkOut):
    if not checkIn or not checkOut:
        return None

    duration = checkOut - checkIn
    return duration


def calculate_average_working_hours(working_hours_list):
    if not working_hours_list:
        return timedelta(seconds=0)

    total_working_hours = sum(working_hours_list, timedelta())
    average_working_hours = total_working_hours / len(working_hours_list)
    rounded_average_hours = round(average_working_hours.total_seconds())  # Round to the nearest second

    return timedelta(seconds=rounded_average_hours)


def check_leaves_func(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    leaves = db.query(Leaves).filter(Leaves.company_id == company_id).filter(Leaves.branch_id == branch_id).filter(
        Leaves.user_id == user_id).filter(Leaves.start_date <= date.today()).filter(
        date.today() <= Leaves.end_date).first()
    if leaves:
        if leaves.leave_status == LeaveStatus.APPROVED:
            if leaves.leave_type == LeaveType.CASUAL:
                user_details = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
                user_details.casual_leaves += 1

            else:
                user_details = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
                user_details.medical_leaves += 1
            db.commit()


def check_in_func(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    check_leaves_func(company_id, branch_id, user_id, db)
    new_attendance = Attendance(company_id=company_id, branch_id=branch_id, user_id=user_id, date=date.today())
    new_attendance.check_in = datetime.now()
    db.add(new_attendance)
    db.commit()

    return ResponseDTO(200, "Check-in successfully",
                       {"check_in": new_attendance.check_in, "check_out": new_attendance.check_out,
                        "average_working_hours": get_average_working_hours(company_id, branch_id, user_id, db)})


def check_out_func(attendance, db=Depends(get_db)):
    if attendance.check_out:
        return ResponseDTO(204, "Attendance already marked for Today",
                           {"check_in": attendance.check_in, "check_out": attendance.check_out,
                            "average_working_hours": get_average_working_hours(attendance.company_id,
                                                                               attendance.branch_id, attendance.user_id,
                                                                               db)})
    else:
        attendance.check_out = datetime.now()
        db.commit()

        return ResponseDTO(200, "Check-out successfully",
                           {"check_in": attendance.check_in, "check_out": attendance.check_out,
                            "average_working_hours": get_average_working_hours(attendance.company_id,
                                                                               attendance.branch_id, attendance.user_id,
                                                                               db)})


def mark_attendance_func(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        user = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if user is None:
            attendance = fetch_attendance_today(company_id, branch_id, user_id, db)

            if attendance:
                return check_out_func(attendance, db)
            else:
                return check_in_func(company_id, branch_id, user_id, db)

        else:
            return ResponseDTO(204, "User not found", {})
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def get_todays_attendance(user_id: int, company_id: int, branch_id: int, db=Depends(get_db)):
    try:
        user = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if user is None:
            attendance = fetch_attendance_today(company_id, branch_id, user_id, db)

            attendance_today = {"check_in": attendance.check_in if attendance else None,
                                "check_out": attendance.check_out if attendance else None,
                                "average_working_hours": get_average_working_hours(company_id, branch_id, user_id, db)}

            return ResponseDTO(200, "Attendance fetched successfully", attendance_today)
        else:
            return ResponseDTO(204, "User not found", {})
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def attendance_history_func(user_id: int, company_id: int, branch_id: int, db=Depends(get_db),
                            u_id: Optional[str] = None):
    try:
        user = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if user is None:
            attendance = (
                db.query(Attendance).filter(Attendance.user_id == (u_id if u_id else user_id)).filter(
                    Attendance.company_id == company_id).filter(Attendance.branch_id == branch_id).all())
            history = []
            for i in attendance:
                history.append({"check_in": i.check_in, "check_out": i.check_out, "date": i.date})

            return ResponseDTO(200, "Attendance fetched successfully", history)
        else:
            return ResponseDTO(204, "User not found", [])
    except Exception as exc:
        return ResponseDTO(204, str(exc), [])


def get_average_working_hours(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    working_hours_list = []
    attendances = db.query(Attendance).filter(Attendance.company_id == company_id,
                                              Attendance.branch_id == branch_id,
                                              Attendance.user_id == user_id,
                                              Attendance.check_in.isnot(None),
                                              Attendance.check_out.isnot(None)).all()

    for attendance in attendances:
        working_hours_list.append(calculate_working_hours(attendance.check_in, attendance.check_out))

    average_working_hours = calculate_average_working_hours(working_hours_list)

    return str(average_working_hours)

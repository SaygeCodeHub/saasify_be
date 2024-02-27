"""Service layer for - Shifts"""
from datetime import datetime

from app.dto.dto_classes import ResponseDTO
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.shifts import Shifts
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.schemas.shifts_schemas import AddShift, GetShifts


def add_shift(shift: AddShift, user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            shift.company_id = company_id
            shift.branch_id = branch_id
            new_shift = Shifts(**shift.model_dump())
            db.add(new_shift)
            db.commit()
            return ResponseDTO(200, "Shift added!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def fetch_all_shifts(user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            shifts = db.query(Shifts).filter(Shifts.company_id == company_id).filter(
                Shifts.branch_id == branch_id).all()
            result = [GetShifts(shift_id=shift.shift_id, shift_name=shift.shift_name, start_time=shift.start_time,
                                end_time=shift.end_time)
                      for shift in shifts
                      ]

            return ResponseDTO(200, "Shifts fetched!", result)
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def change_shift_info(new_shift_info, user_id, company_id, branch_id, shift_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            shift_query = db.query(Shifts).filter(Shifts.shift_id == shift_id)
            shift_query.update({"shift_name": new_shift_info.shift_name, "start_time": new_shift_info.start_time,
                                "end_time": new_shift_info.end_time, "modified_on": datetime.now(),
                                "modified_by": user_id})
            db.commit()

            return ResponseDTO(200, "Shift updated!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def remove_shift(user_id, company_id, branch_id, shift_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            db.query(Shifts).filter(Shifts.shift_id == shift_id).delete()
            db.commit()

            return ResponseDTO(200, "Shift deleted!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def assign_shift_to_employee(user_id, company_id, branch_id, u_id, shift_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            shift_assignment_query = db.query(UserCompanyBranch).filter(
                UserCompanyBranch.company_id == company_id).filter(UserCompanyBranch.branch_id == branch_id).filter(
                UserCompanyBranch.user_id == u_id)
            shift_assignment_query.update(
                {"shift_id": shift_id, "modified_by": user_id, "modified_on": datetime.now()})
            db.commit()
            return ResponseDTO(200, "Shift assigned!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

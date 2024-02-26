"""Service layer for Users"""
from datetime import datetime, timedelta

import holidays
from fastapi import Depends
from sqlalchemy import extract

from app.v2_0.HRMS.application.service.employee_service import get_designation_name
from app.v2_0.HRMS.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.attendance import Attendance
from app.v2_0.HRMS.domain.models.user_auth import UsersAuth
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.models.user_finance import UserFinance
from app.v2_0.dto.dto_classes import ResponseDTO
from app.v2_0.infrastructure.database import get_db


def calculate_rollout(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            salary_rollout = calculate_salary_rollout(branch_id, db)
            return ResponseDTO(200, "Salary Rollout for each employee", salary_rollout)

        else:
            return check

    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def calculate_salary(finance, working_days, db=Depends(get_db)):
    basic_salary = finance.basic_salary
    daily_salary = basic_salary / 30
    total_deductions = finance_deduction(finance, db, working_days)
    allowances = finance.BOA + finance.bonus + finance.PF + finance.performance_bonus + finance.gratuity
    total_allowances = allowances

    net_salary = daily_salary * 30 + total_allowances - total_deductions
    return net_salary


def calculate_working_days_in_month():
    india_holidays = holidays.country_holidays(country='IN', years=datetime.now().year)
    start_date = datetime(datetime.now().year, datetime.now().month, 1)
    end_date = start_date.replace(day=1, month=datetime.now().month + 1) - timedelta(days=1)
    working_days = sum(1 for day in range((end_date - start_date).days + 1)
                       if (start_date + timedelta(day)).weekday() < 5
                       and (start_date + timedelta(day)) not in india_holidays)
    return working_days


# Example function to calculate salary rollout for all employees
def calculate_salary_rollout(branch_id: int, db=Depends(get_db)):
    # Calculate working days in the month
    working_days = calculate_working_days_in_month()

    # Retrieve employee information and calculate salary for each employee
    employees = (
        db.query(UserDetails, UsersAuth, UserCompanyBranch, UserFinance)
        .join(UserCompanyBranch, UserDetails.user_id == UserCompanyBranch.user_id)
        .join(UsersAuth, UsersAuth.user_id == UserDetails.user_id)
        .join(UserFinance, UserFinance.user_id == UserDetails.user_id)
        .filter(UserCompanyBranch.branch_id == branch_id))
    salary_rollout = []
    total = 0.00
    all_rolled_out = False
    for details, auth, ucb, finance in employees:  # Assuming employee IDs start from 1 and end at 2
        if auth:
            net_salary = calculate_salary(finance, working_days, db)
            salary_rollout.append({"employee_id": auth.user_id,
                                   "name": details.first_name + " " + details.last_name if details.first_name and details.last_name else "Invited User",
                                   "user_contact": details.user_contact, "user_email": auth.user_email,
                                   "designations": get_designation_name(ucb.designations),
                                   "current_address": details.current_address, "payroll": round(net_salary, 2),
                                   "is_rolled_out": finance.is_rolled_out})
            total += net_salary
            print(auth.user_id, "user_id")
            if employees.filter(UserFinance.is_rolled_out == False).count() == 0:
                all_rolled_out = True
    rollout = {"total_salary_rollout": round(total, 2), "all_rolled_out": all_rolled_out,
               "salary_rollout": salary_rollout}
    return rollout


def rollout_all(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            employees = (
                db.query(UserDetails, UsersAuth, UserCompanyBranch, UserFinance)
                .join(UserCompanyBranch, UserDetails.user_id == UserCompanyBranch.user_id)
                .join(UsersAuth, UsersAuth.user_id == UserDetails.user_id)
                .join(UserFinance, UserFinance.user_id == UserDetails.user_id)
                .filter(UserCompanyBranch.branch_id == branch_id))
            for details, auth, ucb, finance in employees:
                if auth:
                    if finance.is_rolled_out == False:
                        employee_rollout(finance, db)
            return ResponseDTO(200, "Salary Rolled Out for all Employees", {})

        else:
            return check

    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def rollout_individual(company_id: int, branch_id: int, user_id: int, u_id: str, db=Depends(get_db)):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            employee_finance = (db.query(UserFinance, UserCompanyBranch)
                                .join(UserFinance, UserFinance.user_id == UserCompanyBranch.user_id)
                                .filter(UserCompanyBranch.user_id == u_id)
                                .filter(UserCompanyBranch.branch_id == branch_id))
            for finance, ucb in employee_finance:
                if finance.is_rolled_out == False:
                    employee_rollout(finance, db)
                    return ResponseDTO(200, "Salary Rolled Out successfully!", {})
                else:
                    return ResponseDTO(204, "Salary already rolled out!", {})
            else:
                return ResponseDTO(204, "Employee not found", {})

        else:
            return check

    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def employee_rollout(employee_finance, db=Depends(get_db)):
    employee_finance.deduction = 0.0
    employee_finance.is_rolled_out = True
    db.commit()


def calculate_deduction(company_id: int, branch_id: int, user_id: int, u_id: str, db=Depends(get_db)):
    # try:
    check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

    if check is None:
        final_pay = 0.0
        working_days = calculate_working_days_in_month()
        if u_id:
            employee = (db.query(UserDetails, UsersAuth, UserCompanyBranch, UserFinance)
                        .join(UserCompanyBranch, UserDetails.user_id == UserCompanyBranch.user_id)
                        .join(UsersAuth, UsersAuth.user_id == UserDetails.user_id)
                        .join(UserFinance, UserFinance.user_id == UserDetails.user_id)
                        .filter(UserCompanyBranch.branch_id == branch_id).filter(UsersAuth.user_id == u_id))
            total_deductions = 0.0
            for details, auth, ucb, finance in employee:
                if finance:
                    pay = finance.BOA + finance.bonus + finance.PF + finance.performance_bonus + finance.gratuity + finance.basic_salary
                    total_deductions = finance_deduction(finance, db, working_days)
                    final_pay = pay - total_deductions
            return ResponseDTO(200, "Deduction calculated successfully!", {"final_pay": round(final_pay, 2)})
        else:
            employees = (
                db.query(UserDetails, UsersAuth, UserCompanyBranch, UserFinance)
                .join(UserCompanyBranch, UserDetails.user_id == UserCompanyBranch.user_id)
                .join(UsersAuth, UsersAuth.user_id == UserDetails.user_id)
                .join(UserFinance, UserFinance.user_id == UserDetails.user_id)
                .filter(UserCompanyBranch.branch_id == branch_id))
            total_deductions = 0.0
            for details, auth, ucb, finance in employees:
                if finance:
                    pay = finance.BOA + finance.bonus + finance.PF + finance.performance_bonus + finance.gratuity + finance.basic_salary
                    total_deductions += finance_deduction(finance, db, working_days)
                    final_pay += (pay - total_deductions)
            return ResponseDTO(200, "Deduction calculated successfully!", {"final_pay": round(final_pay, 2)})
    else:
        return check


# except Exception as exc:
#     db.rollback()
#     return ResponseDTO(204, str(exc), {})

def finance_deduction(finance, db, working_days):
    total_deductions = 0.0
    if finance.is_rolled_out == False:
        timesheet = db.query(Attendance).filter(Attendance.user_id == finance.user_id,
                                                extract('month',
                                                        Attendance.date) == datetime.now().month).all()
        daily_salary = finance.basic_salary / 30
        if len(timesheet) < working_days:
            leaves = db.query(UserDetails).filter(UserDetails.user_id == finance.user_id).first()
            if leaves.casual_leaves == 0 and leaves.medical_leaves == 0:
                for i in range(working_days - len(timesheet)):
                    total_deductions += daily_salary
    return total_deductions

"""Service layer for Home screen data"""
from datetime import datetime

from sqlalchemy import select

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.service.leave_service import get_authorized_leave_requests, format_pending_leaves
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.domain.models.branches import Branches
from app.v2_0.domain.models.enums import LeaveStatus, Features, DesignationEnum
from app.v2_0.domain.models.leaves import Leaves
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.models.user_finance import UserFinance
from app.v2_0.domain.schemas.branch_schemas import GetBranch
from app.v2_0.domain.schemas.home_screen_schemas import HomeScreenAPI, Salaries
from app.v2_0.domain.schemas.leaves_schemas import GetPendingLeaves


def get_home_screen_branches(user_id, db):
    branches_query = select(UserCompanyBranch.branch_id, UserCompanyBranch.accessible_features,
                            UserCompanyBranch.accessible_modules, Branches.branch_name).select_from(
        UserCompanyBranch).join(Branches, UserCompanyBranch.branch_id == Branches.branch_id).filter(
        UserCompanyBranch.user_id == user_id)
    branches = db.execute(branches_query)

    branches_resp = [GetBranch(branch_name=branch.branch_name, branch_id=branch.branch_id,
                               accessible_modules=branch.accessible_modules,
                               accessible_features=branch.accessible_features)
                     for branch in branches
                     ]
    return branches_resp


def get_home_screen_pending_leaves(user_id, db):
    pending_leaves = db.query(Leaves).filter(Leaves.leave_status == LeaveStatus.PENDING).all()
    filtered_leaves = get_authorized_leave_requests(pending_leaves, user_id)
    if len(filtered_leaves) != 0:
        return len(filtered_leaves)
    else:
        return 0


def get_monthly_salary_rollout(user_id, branch_id, db):
    user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()
    if Features.HR_SALARY_ROLLOUT in user.accessible_features:
        salary_query = select(UserFinance.salary, UserFinance.deduction).select_from(UserFinance).join(
            UserCompanyBranch,
            UserFinance.user_id == UserCompanyBranch.user_id).filter(
            UserCompanyBranch.branch_id == branch_id)
        # .filter(UserCompanyBranch.designations != [DesignationEnum.OWNER])
        salaries = db.execute(salary_query)

        result = [Salaries(salary=salary.salary, deduction=salary.deduction)
                  for salary in salaries
                  ]

        salary_sum = 0
        for i in range(0, datetime.now().day):
            for x in result:
                salary_sum = salary_sum + x.salary / 30

        total_deduction = 0
        for x in result:
            total_deduction = total_deduction + x.deduction

        return salary_sum - total_deduction
    return 0


def fetch_home_screen_data(user_id, company_id, branch_id, db):
    """Fetches data to be shown on the home screen"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:

            branches = get_home_screen_branches(user_id, db)
            num_of_pending_leaves = get_home_screen_pending_leaves(user_id, db)
            salary_rollout = get_monthly_salary_rollout(user_id, branch_id, db)
            return ResponseDTO(200, "Data fetched!",
                               HomeScreenAPI(branches=branches, pending_leaves=num_of_pending_leaves,
                                             monthly_salary_rollout=salary_rollout))

        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

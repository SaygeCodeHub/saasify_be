"""Service layer for Home screen data"""
from datetime import datetime

from sqlalchemy import select

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.service.leave_service import get_authorized_leave_requests
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.domain.models.branch_settings import BranchSettings
from app.v2_0.domain.models.branches import Branches
from app.v2_0.domain.models.enums import LeaveStatus, Features
from app.v2_0.domain.models.leaves import Leaves
from app.v2_0.domain.models.module_subscriptions import ModuleSubscriptions
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.models.user_finance import UserFinance
from app.v2_0.domain.schemas.branch_schemas import GetBranch
from app.v2_0.domain.schemas.home_screen_schemas import HomeScreenApiResponse, Salaries, IteratedBranchSettings
from app.v2_0.domain.schemas.module_schemas import ModulesMap, FeaturesMap, AvailableModulesMap


def get_home_screen_branches(user_id, db):
    branches_query = (select(UserCompanyBranch.branch_id, Branches.branch_name,
                             BranchSettings.geo_fencing).select_from(
        UserCompanyBranch).join(Branches, UserCompanyBranch.branch_id == Branches.branch_id).join(BranchSettings,
                                                                                                  UserCompanyBranch.branch_id == BranchSettings.branch_id).filter(
        UserCompanyBranch.user_id == user_id))
    branches = db.execute(branches_query)

    branches_resp = [GetBranch(branch_name=branch.branch_name, branch_id=branch.branch_id)
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
        salary_query = select(UserFinance.basic_salary, UserFinance.deduction).select_from(UserFinance).join(
            UserCompanyBranch,
            UserFinance.user_id == UserCompanyBranch.user_id).filter(
            UserCompanyBranch.branch_id == branch_id)
        # .filter(UserCompanyBranch.designations != [DesignationEnum.OWNER])
        salaries = db.execute(salary_query)

        result = [Salaries(basic_salary=salary.basic_salary, deduction=salary.deduction)
                  for salary in salaries
                  ]

        salary_sum = 0
        for i in range(0, datetime.now().day):
            for x in result:
                salary_sum = salary_sum + x.basic_salary / 30

        total_deduction = 0
        for x in result:
            total_deduction = total_deduction + x.deduction

        return salary_sum - total_deduction
    return 0


def is_authorized_for_salary_rollout(ucb_entry):
    if Features.HR_SALARY_ROLLOUT in ucb_entry.accessible_features:
        return True
    return False


def check_if_statistics(feature_name):
    if feature_name == Features.HR_PENDING_APPROVAL.name or feature_name == Features.HR_SALARY_ROLLOUT.name or feature_name == Features.HR_VIEW_ALL_EMPLOYEES.name:
        return True
    return False


def calculate_value(feature_name, user_id, company_id, branch_id, db):
    flag = check_if_statistics(feature_name)

    if flag:
        if feature_name == Features.HR_PENDING_APPROVAL.name:
            num_of_pending_leaves = get_home_screen_pending_leaves(user_id, db)
            return str(num_of_pending_leaves)
        elif feature_name == Features.HR_SALARY_ROLLOUT.name:
            salary_rollout = get_monthly_salary_rollout(user_id, branch_id, db)
            return str(salary_rollout)
        elif feature_name == Features.HR_VIEW_ALL_EMPLOYEES.name:
            total_employees = db.query(UserCompanyBranch).filter(UserCompanyBranch.branch_id == branch_id).count()
            return str(total_employees)

    else:
        return ""


def get_title(name):
    substring_before_underscore = name.split('_', 1)[0]
    result = "HR" if "HR" in substring_before_underscore else ""
    return result


def fetch_home_screen_data(device_token_obj, user_id, company_id, branch_id, db):
    """Fetches data to be shown on the home screen"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            # Adds the device token of the user with id user_id belonging to branch_id and company_id
            user_query = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).filter(
                UserCompanyBranch.company_id == company_id).filter(
                UserCompanyBranch.branch_id == branch_id)
            user_query.update({"device_token": device_token_obj.device_token})
            db.commit()

            branches = get_home_screen_branches(user_id, db)

            ucb_entry = db.query(UserCompanyBranch).filter(
                UserCompanyBranch.user_id == user_id).filter(UserCompanyBranch.company_id == company_id).filter(
                UserCompanyBranch.branch_id == branch_id).first()

            branch_settings = db.query(BranchSettings).filter(BranchSettings.branch_id == branch_id).first()

            iterated_result = IteratedBranchSettings(
                accessible_features=ucb_entry.accessible_features,
                accessible_modules=ucb_entry.accessible_modules,
                geo_fencing=branch_settings.geo_fencing)

            module_subscription = db.query(ModuleSubscriptions).filter(
                ModuleSubscriptions.company_id == company_id).filter(ModuleSubscriptions.branch_id == branch_id).first()

            accessible_modules = []

            for acm in iterated_result.accessible_modules:
                accessible_modules.append(
                    ModulesMap(module_key=acm.name, module_id=acm.value, title=acm.name, icon="", accessible_features=[
                        FeaturesMap(feature_key=af.name, feature_id=af.value, title=get_title(af.name), icon="",
                                    value=calculate_value(
                                        af.name, user_id, company_id, branch_id, db),
                                    is_statistics=check_if_statistics(af.name))
                        for af in iterated_result.accessible_features]))

            available_module = []
            for avm in module_subscription.module_name:
                available_features = []
                for features in Features:
                    if features.name.startswith(avm.name):
                        print("features.name", features.name)
                        available_features.append(FeaturesMap(feature_key=features.name, feature_id=features.value,
                                                              title=get_title(features.name),
                                                              icon="",
                                                              value=calculate_value(
                                                                  features.name, user_id, company_id, branch_id, db),
                                                              is_statistics=check_if_statistics(features.name)))
                print("available_features", available_features)
                available_module.append(
                    AvailableModulesMap(module_key=avm.name, module_id=avm.value, title=avm.name, icon="",
                                        available_features=available_features))
                print("available_module", available_module)

            result = HomeScreenApiResponse(branches=branches, accessible_modules=accessible_modules,
                                           available_modules=available_module,
                                           geo_fencing=iterated_result.geo_fencing)

            return ResponseDTO(200, "Data fetched!", result)

        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

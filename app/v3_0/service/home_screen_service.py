"""Service layer for Home screen data"""
from datetime import datetime

from sqlalchemy import select

from app.enums.features_enum import Features
from app.enums.leave_status_enum import LeaveStatus
from app.enums.task_status_enum import TaskStatus
from app.v2_0.HRMS.application.service.leave_service import get_authorized_leave_requests
from app.v2_0.HRMS.application.service.task_service import get_assigner_name
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.announcements import Announcements
from app.v2_0.HRMS.domain.models.branch_settings import BranchSettings
from app.v2_0.HRMS.domain.models.branches import Branches
from app.v2_0.HRMS.domain.models.leaves import Leaves
from app.v2_0.HRMS.domain.models.module_subscriptions import ModuleSubscriptions
from app.v2_0.HRMS.domain.models.tasks import Tasks
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.models.user_finance import UserFinance
from app.v2_0.HRMS.domain.schemas.announcement_schemas import GetAnnouncements
from app.v2_0.HRMS.domain.schemas.branch_schemas import GetBranch
from app.v2_0.HRMS.domain.schemas.task_schemas import GetTasksAssignedToMe, GetTasksAssignedByMe
from app.dto.dto_classes import ResponseDTO
from app.v3_0.schemas.home_screen_schemas import Salaries, IteratedBranchSettings, HomeScreenApiResponse
from app.v3_0.schemas.module_schemas import FeaturesMap, ModulesMap, AvailableModulesMap


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
        for x in result:
            salary_sum = salary_sum + x.basic_salary

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
    check_array = [Features.HR_PENDING_APPROVAL.name, Features.HR_SALARY_ROLLOUT.name,
                   Features.HR_VIEW_ALL_EMPLOYEES.name]
    if feature_name in check_array:
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
            rounded_number = round(salary_rollout, 2)
            return f"Rs. {str(rounded_number)}"
        elif feature_name == Features.HR_VIEW_ALL_EMPLOYEES.name:
            total_employees = db.query(UserCompanyBranch).filter(UserCompanyBranch.branch_id == branch_id).all()
            if total_employees:
                count = len(total_employees)
            else:
                count = 0
            return str(count)

    else:
        return ""


def get_title(name):
    split_string = name.split("_", 1)
    parts = split_string[1].lower().split('_')
    result = ' '.join(x.capitalize() for x in parts)
    return result


def get_tasks_assigned_to_me(user_id, db):
    tasks_assigned_to_me = (db.query(Tasks).filter(Tasks.assigned_to == user_id)
                            .order_by(Tasks.task_status != TaskStatus.PENDING).limit(6).all())
    return tasks_assigned_to_me


def get_tasks_assigned_by_me(user_id, db):
    tasks_assigned_by_me = (db.query(Tasks).filter(Tasks.monitored_by == user_id)
                            .order_by(Tasks.task_status != TaskStatus.PENDING).limit(6).all())
    return tasks_assigned_by_me


def fetch_active_announcements(company_id, db):
    active_announcements = db.query(Announcements).filter(Announcements.company_id == company_id).filter(
        Announcements.is_active == "true").all()
    return active_announcements


def get_is_view(feature_name):
    view_array = [Features.HR_ADD_ANNOUNCEMENT.name, Features.HR_ADD_NEW_EMPLOYEE.name, Features.HR_APPLY_LEAVES.name,
                  Features.HR_SHIFT_MANAGEMENT.name]
    if feature_name in view_array:
        return False
    return True


def get_build_screen_endpoint(feature_name):
    endpoint_dict = {Features.HR_ADD_ANNOUNCEMENT.name: "/v3.0/buildAnnouncementForm",
                     Features.HR_ADD_NEW_EMPLOYEE.name: "/v3.0/buildEmployeeForm",
                     Features.HR_APPLY_LEAVES.name: "/v3.0/buildApplyLeaveForm",
                     Features.HR_SHIFT_MANAGEMENT.name: "/v3.0/buildShiftManagementForm",
                     Features.HR_MARK_ATTENDANCE.name: "/v3.0/buildAttendanceTable",
                     Features.HR_PENDING_APPROVAL.name: "/v3.0/buildPendingApprovalTable",
                     Features.HR_SALARY_ROLLOUT.name: "/v3.0/buildSalaryTable",
                     Features.HR_VIEW_ALL_EMPLOYEES.name: "/v3.0/buildEmployeesTable",
                     Features.HR_MY_LEAVES.name: "/v3.0/buildMyLeavesTable",
                     Features.HR_TIMESHEET.name: "/v3.0/buildTimesheetTable"}
    return endpoint_dict.get(feature_name)


def fetch_home_screen_data(device_token_obj, user_id, company_id, branch_id, db):
    """Fetches data to be shown on the home screen"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            # Adds the device token of the user with id user_id belonging to branch_id and company_id
            user_query = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).filter(
                UserCompanyBranch.company_id == company_id).filter(
                UserCompanyBranch.branch_id == branch_id)
            user_query.update(
                {"device_token": device_token_obj.device_token, "modified_by": user_id, "modified_on": datetime.now()})
            db.commit()

            branches = get_home_screen_branches(user_id, db)

            ucb_entry = db.query(UserCompanyBranch).filter(
                UserCompanyBranch.user_id == user_id).filter(UserCompanyBranch.company_id == company_id).filter(
                UserCompanyBranch.branch_id == branch_id).first()
            user_data = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()

            branch_settings = db.query(BranchSettings).filter(BranchSettings.branch_id == branch_id).first()

            iterated_result = IteratedBranchSettings(
                accessible_features=ucb_entry.accessible_features,
                accessible_modules=ucb_entry.accessible_modules,
                geo_fencing=branch_settings.geo_fencing)

            module_subscription = db.query(ModuleSubscriptions).filter(
                ModuleSubscriptions.company_id == company_id).filter(ModuleSubscriptions.branch_id == branch_id).first()

            accessible_modules = []

            for acm in iterated_result.accessible_modules:
                accessible_features = []
                for features in iterated_result.accessible_features:
                    if features.name.startswith(acm.name):
                        accessible_features.append(FeaturesMap(feature_key=features.name, feature_id=features.value,
                                                               title=get_title(features.name),
                                                               icon="",
                                                               value=calculate_value(
                                                                   features.name, user_id, company_id, branch_id, db),
                                                               is_statistics=check_if_statistics(features.name),
                                                               is_view=get_is_view(features.name),
                                                               build_screen_endpoint=get_build_screen_endpoint(
                                                                   features.name)))
                accessible_modules.append(
                    ModulesMap(module_key=acm.name, module_id=acm.value, title=acm.name, icon="",
                               accessible_features=accessible_features))

            available_module = []
            for avm in module_subscription.module_name:
                available_features = []
                for features in Features:
                    if features.name.startswith(avm.name):
                        available_features.append(FeaturesMap(feature_key=features.name, feature_id=features.value,
                                                              title=get_title(features.name),
                                                              icon="",
                                                              value=calculate_value(
                                                                  features.name, user_id, company_id, branch_id, db),
                                                              is_statistics=check_if_statistics(features.name),
                                                              is_view=get_is_view(features.name),
                                                              build_screen_endpoint=get_build_screen_endpoint(
                                                                  features.name)))
                available_module.append(
                    AvailableModulesMap(module_key=avm.name, module_id=avm.value, title=avm.name, icon="",
                                        available_features=available_features))

            my_tasks = get_tasks_assigned_to_me(user_id, db)
            tasks_assigned_to_me = []
            for task in my_tasks:
                tasks_assigned_to_me.append(
                    GetTasksAssignedToMe(task_id=task.task_id, title=task.title, task_description=task.task_description,
                                         due_date=task.due_date,
                                         priority=task.priority, assigned_by=get_assigner_name(task.monitored_by, db),
                                         task_status=task.task_status.name, comment=task.comment))

            tasks_by_me = get_tasks_assigned_by_me(user_id, db)
            tasks_assigned_by_me = [
                GetTasksAssignedByMe(task_id=task.task_id, title=task.title, task_description=task.task_description,
                                     due_date=task.due_date,
                                     priority=task.priority, assigned_to=get_assigner_name(task.assigned_to, db),
                                     task_status=task.task_status.name, comment=task.comment)
                for task in tasks_by_me]

            announcements = fetch_active_announcements(company_id, db)
            active_announcements = [GetAnnouncements(id=announcement.announcement_id, due_date=announcement.due_date,
                                                     description=announcement.description,
                                                     is_active=announcement.is_active)
                                    for announcement in announcements]

            result = HomeScreenApiResponse(branches=branches, accessible_modules=accessible_modules,
                                           available_modules=available_module,
                                           geo_fencing=iterated_result.geo_fencing,
                                           tasks_assigned_to_me=tasks_assigned_to_me,
                                           tasks_assigned_by_me=tasks_assigned_by_me,
                                           announcements=active_announcements,
                                           gender=user_data.gender if user_data else None)

            return ResponseDTO(200, "Data fetched!", result)

        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

"""Service layer for - Task Management"""
import asyncio

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.service.push_notification_service import send_task_assigned_notification
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.domain.models.tasks import Tasks
from app.v2_0.domain.models.user_details import UserDetails
from app.v2_0.domain.schemas.task_schemas import GetMyTasks, AssignerData


def assign_task(assigned_task, user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            assigned_task.monitored_by = user_id
            assigned_task.branch_id = branch_id
            assigned_task.company_id = company_id
            new_task = Tasks(**assigned_task.model_dump())
            db.add(new_task)
            db.commit()

            asyncio.run(send_task_assigned_notification(assigned_task, user_id, company_id, branch_id, db))

            return ResponseDTO(200, "Task Assigned!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def get_assigner_name(monitored_by, db):
    assigner = db.query(UserDetails).filter(UserDetails.user_id == monitored_by).first()

    return AssignerData(id=monitored_by, name=assigner.first_name + " " + assigner.last_name)


def fetch_my_tasks(user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            my_tasks = db.query(Tasks).filter(Tasks.company_id == company_id).filter(
                Tasks.branch_id == branch_id).filter(Tasks.assigned_to == user_id).all()

            result = [GetMyTasks(title=task.title, task_description=task.task_description, due_date=task.due_date,
                                 priority=task.priority, assigned_by=get_assigner_name(task.monitored_by, db),
                                 task_status=task.task_status.name)
                      for task in my_tasks
                      ]
            return ResponseDTO(200, "Tasks fetched!", result)
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

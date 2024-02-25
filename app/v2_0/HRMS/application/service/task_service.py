"""Service layer for - Task Management"""
import asyncio
from datetime import datetime

from app.v2_0.HRMS.application.service.push_notification_service import send_task_assigned_notification, \
    send_task_updated_notification
from app.v2_0.HRMS.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.tasks import Tasks
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.schemas.task_schemas import GetTasksAssignedToMe, Data, GetTasksAssignedByMe
from app.v2_0.dto.dto_classes import ResponseDTO


def assign_task(assigned_task, user_id, company_id, branch_id, db):
    """Assigns a task to an individual"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
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
    if assigner.first_name is None or assigner.last_name is None:
        assigner.first_name = "Some"
        assigner.last_name = "Employee"

    return Data(id=monitored_by, name=assigner.first_name + " " + assigner.last_name)


def fetch_my_tasks(user_id, company_id, branch_id, db):
    """Fetches tasks assigned to me and assigned by me"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            tasks_assigned_to_me = db.query(Tasks).filter(Tasks.company_id == company_id).filter(
                Tasks.branch_id == branch_id).filter(Tasks.assigned_to == user_id).all()

            array_of_tasks_assigned_to_me = [
                GetTasksAssignedToMe(task_id=task.task_id, title=task.title, task_description=task.task_description,
                                     due_date=task.due_date,
                                     priority=task.priority, assigned_by=get_assigner_name(task.monitored_by, db),
                                     task_status=task.task_status.name, comment=task.comment) for task in
                tasks_assigned_to_me]

            tasks_assigned_by_me = db.query(Tasks).filter(Tasks.company_id == company_id).filter(
                Tasks.branch_id == branch_id).filter(Tasks.monitored_by == user_id).all()

            array_of_tasks_assigned_by_me = [
                GetTasksAssignedByMe(task_id=task.task_id, title=task.title, task_description=task.task_description,
                                     due_date=task.due_date,
                                     priority=task.priority, assigned_to=get_assigner_name(task.assigned_to, db),
                                     task_status=task.task_status.name, comment=task.comment)
                for task in tasks_assigned_by_me]

            return ResponseDTO(200, "Tasks fetched!", {"tasks_assigned_to_me": array_of_tasks_assigned_to_me,
                                                       "tasks_assigned_by_me": array_of_tasks_assigned_by_me})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def change_task_status(updated_task, user_id, company_id, branch_id, db):
    """Updates the status of the task - DONE/CLOSED"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:

            query = db.query(Tasks).filter(Tasks.task_id == updated_task.task_id)
            query.update({"completion_date": updated_task.completion_date, "task_status": updated_task.task_status,
                          "comment": updated_task.comment, "modified_by": user_id, "modified_on": datetime.now()})
            asyncio.run(send_task_updated_notification(updated_task, user_id, company_id, branch_id, db))
            db.commit()

            return ResponseDTO(200, "Task updated successfully!", {})

        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def change_task(updated_task, user_id, company_id, branch_id, db):
    """Edit the task details"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:

            query = db.query(Tasks).filter(Tasks.task_id == updated_task.task_id)
            query.update(updated_task.__dict__)
            db.commit()

            return ResponseDTO(200, "Task Edited Successfully!", {})

        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

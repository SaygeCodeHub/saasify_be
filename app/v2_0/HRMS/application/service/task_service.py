"""Service layer for - Task Management"""
from datetime import datetime

from app.dto.dto_classes import ResponseDTO
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.application.service.push_notification_service import send_task_assigned_notification, \
    send_task_updated_notification
from app.v2_0.HRMS.domain.models.tasks import Tasks
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.schemas.task_schemas import GetTasksAssignedToMe, Data, GetTasksAssignedByMe


async def assign_task(assigned_task, user_id, company_id, branch_id, db):
    """Assigns a task to an individual"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            assigned_task.branch_id = branch_id
            assigned_task.company_id = company_id
            new_task = Tasks(**assigned_task.model_dump())
            db.add(new_task)
            db.commit()

            await send_task_assigned_notification(assigned_task, user_id, company_id, branch_id, db)

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
                Tasks.branch_id == branch_id).filter(Tasks.assigned_to == user_id).order_by(
                Tasks.task_status != "PENDING").all()
            array_of_tasks_assigned_to_me = []
            for task in tasks_assigned_to_me:
                array_of_tasks_assigned_to_me.append(
                    GetTasksAssignedToMe(task_id=task.task_id, title=task.title, task_description=task.task_description,
                                         due_date=task.due_date,
                                         priority=task.priority, assigned_by=get_assigner_name(task.monitored_by, db),
                                         task_status=task.task_status.name, comment=task.comment))

            tasks_assigned_by_me = db.query(Tasks).filter(Tasks.company_id == company_id).filter(
                Tasks.branch_id == branch_id).filter(Tasks.monitored_by == user_id).order_by(
                Tasks.task_status != "PENDING").all()

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


async def change_task_status(updated_task, user_id, company_id, branch_id, db):
    """Updates the status of the task - DONE/CLOSED"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:

            query = db.query(Tasks).filter(Tasks.task_id == updated_task.task_id)
            if updated_task.task_status == "DONE":
                query.update({"completion_date": datetime.now(), "task_status": updated_task.task_status,
                              "comment": updated_task.comment, "modified_by": user_id, "modified_on": datetime.now()})

            query.update({"task_status": updated_task.task_status,
                          "comment": updated_task.comment, "modified_by": user_id, "modified_on": datetime.now()})

            await send_task_updated_notification(updated_task, user_id, company_id, branch_id, db)
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
            updated_task.branch_id = branch_id
            updated_task.company_id = company_id
            query = db.query(Tasks).filter(Tasks.task_id == updated_task.task_id)
            query.update({"title": updated_task.title, "task_description": updated_task.task_description,
                          "assigned_to": updated_task.assigned_to, "monitored_by": updated_task.monitored_by,
                          "due_date": updated_task.due_date, "priority": updated_task.priority,
                          "comment": updated_task.comment, "company_id": updated_task.company_id,
                          "branch_id": updated_task.branch_id, "modified_by": user_id, "modified_on": datetime.now()})
            db.commit()

            return ResponseDTO(200, "Task Edited Successfully!", {})

        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

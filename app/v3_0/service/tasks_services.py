from typing import Type

from fastapi import Depends

from app.custom_exceptions import MissingRequiredFieldError
from app.dto.dto_classes import ResponseDTO
from app.infrastructure.database import get_db, Base
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.application.service.employee_service import employees_list
from app.v2_0.HRMS.domain.models.tasks import Tasks
from app.v2_0.HRMS.domain.schemas.task_schemas import AssignTask
from app.v3_0.forms.add_task_form import add_tasks
from app.v3_0.schemas.form_schema import DropdownOption, DropdownField, DynamicForm


def tasks_employee_dropdown(branch_id: int, db=Depends(get_db)):
    """Fetcha all employees for monitored_by and assigned_to dropdowns"""
    dropdown_options = []
    employees = employees_list(branch_id, db)
    for employee in employees:
        dropdown_options.append(
            DropdownOption(label=employee['user_email'], value=employee['employee_id']))
    return DropdownField(
        options=dropdown_options)


def add_dropdown_field_to_schema(schema, column_name, dropdown_field):
    # Navigate through the schema hierarchy to find the appropriate location
    for section in schema.sections:
        for field_group in section.row:
            for field in field_group.fields:
                if field.column_name == column_name:
                    # Set the dropdown_field at the found location
                    field.dropdown_field = dropdown_field
                    return  # Stop searching after setting the parameter


def plot_tasks_form(branch_id: int, db=Depends(get_db)):
    try:
        """The below step is to fetch the data of dropdowns that need an API call"""
        add_tasks.sections[0].row[1].fields[0].dropdown_field = tasks_employee_dropdown(branch_id, db)
        add_tasks.sections[0].row[1].fields[1].dropdown_field = tasks_employee_dropdown(branch_id, db)

        """Another way of doing the above step"""
        # add_dropdown_field_to_schema(add_tasks, 'monitored_by', tasks_employee_dropdown(branch_id, db))
        # add_dropdown_field_to_schema(add_tasks, 'assigned_to', tasks_employee_dropdown(branch_id, db))
        return ResponseDTO(200, "Form plotted!", add_tasks)
    except Exception as e:
        return ResponseDTO(204, str(e), {})
    finally:
        db.close()


def map_to_model(form: DynamicForm, mapped_values, model: Type[Base]):
    """Function to get column names and respected values in a map
    Still in testing will be moved to app_util"""

    for section in form.sections:
        for field_group in section.row:
            for field in field_group.fields:
                column_name = field.column_name
                if column_name and hasattr(model, column_name):
                    if field.required:
                        if field.user_selection:
                            if field.user_selection.user_selected_date is None and field.user_selection.text_value is None and field.user_selection.user_selected_option_id is None:
                                raise MissingRequiredFieldError(f"Required field '{field.label}' is missing input.")
                            value = field.user_selection.user_selected_date or field.user_selection.text_value or field.user_selection.user_selected_option_id
                        else:
                            raise MissingRequiredFieldError(f"Required field '{field.label}' is missing input.")
                    else:
                        value = None
                    mapped_values[column_name] = value

    return mapped_values


def add_dynamic_tasks(task: DynamicForm, company_id: int, branch_id: int, user_id: int, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if check is None:
            """add the fetched map of column names and values to schema"""
            new_task = AssignTask(**map_to_model(task, {"company_id": company_id, "branch_id": branch_id}, Tasks()))

            new_task_data = Tasks(**new_task.model_dump())
            db.add(new_task_data)
            db.commit()
            return ResponseDTO(200, "Task added!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
    finally:
        db.close()

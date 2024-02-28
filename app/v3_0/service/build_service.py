"""Service layer for building forms and tables"""
from datetime import datetime

from app.dto.dto_classes import ResponseDTO
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.announcements import Announcements
from app.v3_0.forms.add_announcement_form import add_announcements
from app.v3_0.schemas.form_schema import DynamicForm


def plot_announcement_form():
    return ResponseDTO(200, "Form plotted!", add_announcements)


def add_dynamic_announcements(announcement: DynamicForm, user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if check is None:
            new_announcement = Announcements(company_id=company_id,
                                             due_date=announcement.sections[0].fields[0].row_fields[
                                                 0].user_selection.user_selected_date,
                                             description=announcement.sections[0].fields[1].row_fields[
                                                 0].user_selection.text_value)
            # print(new_announcement.__dict__)
            db.add(new_announcement)
            db.commit()
            return ResponseDTO(200, "Announcement added!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def get_bool_value(announcement, user_selected_option_id):
    return announcement.sections[0].fields[0].row_fields[
        1].dropdown_field.options[user_selected_option_id - 1].value


def change_dynamic_announcement_data(announcement: DynamicForm, user_id, company_id, branch_id, announcement_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if check is None:
            announcement_query = db.query(Announcements).filter(Announcements.announcement_id == announcement_id)
            announcement_query.update({"due_date": announcement.sections[0].fields[0].row_fields[
                0].user_selection.user_selected_date, "description": announcement.sections[0].fields[1].row_fields[
                0].user_selection.text_value,
                                       "is_active": get_bool_value(announcement,
                                                                   announcement.sections[0].fields[0].row_fields[
                                                                       1].user_selection.user_selected_option_id),
                                       "modified_by": user_id,
                                       "modified_on": datetime.now()})
            db.commit()
            # print(int(announcement.sections[0].fields[0].row_fields[
            #               1].user_selection.text_value))
            return ResponseDTO(200, "Announcement updated!", {})
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

"""Service layer for - Announcements"""
from datetime import datetime

from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.announcements import Announcements
from app.v2_0.HRMS.domain.schemas.announcement_schemas import GetAnnouncements, AddAnnouncement
from app.dto.dto_classes import ResponseDTO
from app.v3_0.schemas.form_schema import DynamicForm


def add_announcements(announcement, user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if check is None:
            announcement.company_id = company_id
            new_announcement = Announcements(**announcement.model_dump())
            db.add(new_announcement)
            db.commit()
            return ResponseDTO(200, "Announcement added!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def fetch_announcements(user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if check is None:
            announcements = db.query(Announcements).filter(Announcements.company_id == company_id).all()
            result = [GetAnnouncements(id=announcement.announcement_id, due_date=announcement.due_date,
                                       description=announcement.description,
                                       is_active=announcement.is_active)
                      for announcement in announcements
                      ]
            return ResponseDTO(200, "Announcements fetched!", result)
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def change_announcement_data(announcement, user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if check is None:
            announcement_query = db.query(Announcements).filter(Announcements.announcement_id == announcement.id)
            announcement_query.update({"due_date": announcement.due_date, "description": announcement.description,
                                       "is_active": announcement.is_active, "modified_by": user_id,
                                       "modified_on": datetime.now()})
            db.commit()
            return ResponseDTO(200, "Announcement updated!", {})
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def remove_announcement(announcement_id, user_id, company_id, branch_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)
        if check is None:
            db.query(Announcements).filter(Announcements.announcement_id == announcement_id).delete()
            db.commit()
            return ResponseDTO(200, "Announcement deleted!", {})
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

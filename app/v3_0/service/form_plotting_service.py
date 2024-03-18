"""Contains methods that plot forms"""
from fastapi import Depends

from app.dto.dto_classes import ResponseDTO
from app.infrastructure.database import get_db
from app.v3_0.forms.announcement_form import add_announcements
from app.v3_0.forms.category_form import add_category_form


def plot_announcement_form(db=Depends(get_db)):
    try:
        return ResponseDTO(200, "Form plotted!", add_announcements)
    except Exception as e:
        return ResponseDTO(204, str(e), {})
    finally:
        db.close()


def plot_category_form():
    return ResponseDTO(200, "Form plotted!", add_category_form)

"""Contains methods that plot forms"""
from app.dto.dto_classes import ResponseDTO
from app.v3_0.forms.announcement_form import add_announcements
from app.v3_0.forms.category_form import add_category_form


def plot_announcement_form():
    return ResponseDTO(200, "Form plotted!", add_announcements)


def plot_category_form():
    return ResponseDTO(200, "Form plotted!", add_category_form)

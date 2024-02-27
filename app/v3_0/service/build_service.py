"""Service layer for building forms and tables"""
from app.dto.dto_classes import ResponseDTO
from app.v3_0.forms.add_announcement_form import add_announcements


def plot_announcement_form():
    return ResponseDTO(200, "Form plotted!", add_announcements)

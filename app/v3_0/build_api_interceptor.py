"""This file contains all the APIs that will be called for plotting forms and tables"""
from fastapi import APIRouter

from app.v3_0.service.build_service import plot_announcement_form

router = APIRouter()


@router.get("/v3.0/buildAnnouncementForm")
def build_announcement_form():
    return plot_announcement_form()

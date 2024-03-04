"""This file contains all the APIs that will be called for plotting forms and tables"""
from typing import Optional

from fastapi import APIRouter, Depends

from app.infrastructure.database import get_db
from app.v3_0.schemas.form_schema import DynamicForm
from app.v3_0.schemas.utility_schemas import DeviceToken
from app.v3_0.service.build_service import add_dynamic_announcements, \
    change_dynamic_announcement_data, fetch_by_id
from app.v3_0.service.category_service import add_category, modify_category
from app.v3_0.service.form_plotting_service import plot_announcement_form, plot_category_form, plot_product_form
from app.v3_0.service.home_screen_service import fetch_home_screen_data
from app.v3_0.service.product_service import add_product, modify_product

router = APIRouter()

"""----------------------------------------------Form building  APIs-------------------------------------------------------------------"""


@router.get("/v3.0/buildAnnouncementForm")
def build_announcement_form():
    return plot_announcement_form()


@router.get("/v3.0/buildCategoryForm")
def build_category_form():
    return plot_category_form()


@router.get("/v3.0/{company_id}/{branch_id}/{user_id}/buildProductForm")
def build_product_form(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return plot_product_form(company_id, branch_id, user_id, db)


"""----------------------------------------------Category related APIs-------------------------------------------------------------------"""


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/addCategory")
def create_category(category: DynamicForm, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return add_category(category, company_id, branch_id, user_id, db)


@router.put("/v3.0/{company_id}/{branch_id}/{user_id}/updateCategory/{cat_id}")
def update_category(category: DynamicForm, cat_id: int, company_id: int, branch_id: int, user_id: int,
                    db=Depends(get_db)):
    return modify_category(category, cat_id, company_id, branch_id, user_id, db)


"""----------------------------------------------Product related APIs-------------------------------------------------------------------"""


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/addProduct")
def create_product(product: DynamicForm, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return add_product(product, company_id, branch_id, user_id, db)


@router.put("/v3.0/{company_id}/{branch_id}/{user_id}/updateProduct/{prod_id}")
def update_product(product: DynamicForm, prod_id: int, company_id: int, branch_id: int, user_id: int,
                   db=Depends(get_db)):
    return modify_product(product, prod_id, company_id, branch_id, user_id, db)


"""----------------------------------------------User related APIs-------------------------------------------------------------------"""


@router.get("/v3.0/{company_id}/{branch_id}/{user_id}/getUser/{u_id}")
def get_user_by_id(u_id: int, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    """u_id is the id of the person being fetched"""
    return fetch_by_id(u_id, user_id, company_id, branch_id, db)


"""----------------------------------------------Announcements related APIs-------------------------------------------------------------------"""


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/addAnnouncements")
def create_announcements(announcement: DynamicForm, user_id: int, company_id: int, branch_id: int,
                         db=Depends(get_db)):
    return add_dynamic_announcements(announcement, user_id, company_id, branch_id, db)


@router.put("/v3.0/{company_id}/{branch_id}/{user_id}/updateAnnouncements")
def update_announcements(announcement: DynamicForm, user_id: int, company_id: int, branch_id: int,
                         announcement_id: Optional[str] = None,
                         db=Depends(get_db)):
    return change_dynamic_announcement_data(announcement, user_id, company_id, branch_id, announcement_id, db)


"""----------------------------------------------Home Screen API-------------------------------------------------------------------"""


@router.post("/v3.0/{company_id}/{branch_id}/{user_id}/initializeApi")
def get_home_screen_data(device_token_obj: DeviceToken, user_id: int, company_id: int, branch_id: int,
                         db=Depends(get_db)):
    return fetch_home_screen_data(device_token_obj, user_id, company_id, branch_id, db)

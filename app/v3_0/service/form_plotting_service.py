"""Contains methods that plot forms"""
from collections import namedtuple

from app.dto.dto_classes import ResponseDTO
from app.enums.unit_enum import Unit
from app.v2_0.POS.domain.schemas.variant_schemas import UnitEnumSchema
from app.v3_0.forms.announcement_form import add_announcements_form
from app.v3_0.forms.category_form import add_category_form
from app.v3_0.forms.product_form import send_add_products_form
from app.v3_0.schemas.category_schemas import ResponseRequirements
from app.v3_0.service.category_service import fetch_category_with_products


def plot_announcement_form():
    return ResponseDTO(200, "Form plotted!", add_announcements_form)


def plot_category_form():
    return ResponseDTO(200, "Form plotted!", add_category_form)


def plot_product_form(company_id, branch_id, user_id, db):
    req = ResponseRequirements
    req.are_products_required = False
    categories_response = fetch_category_with_products(req, company_id, branch_id, user_id,
                                                       db)
    UnitInfo = namedtuple('UnitInfo', ['name', 'value'])
    units = [UnitInfo(member.name, member.value) for member in Unit]
    unit_array = [UnitEnumSchema(unit_name=unit.name, unit_value=unit.value)
                  for unit in units]
    return ResponseDTO(200, "Form plotted!", send_add_products_form(categories_response.data, unit_array))

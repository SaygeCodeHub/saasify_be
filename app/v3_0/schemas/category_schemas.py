"""Schemas for Model - Categories"""
from typing import List

from pydantic import BaseModel

from app.v3_0.schemas.modifier_schemas import Modifier
from app.v3_0.schemas.product_schemas import GetProducts


class UpdateCategory(Modifier):
    name: str
    description: str


class AddCategory(UpdateCategory):
    company_id: int = None
    branch_id: int = None


class ResponseRequirements(BaseModel):
    are_products_required: bool = False


class GetCategories(BaseModel):
    name: str
    description: str
    category_id: int


class GetCategoriesWithProducts(GetCategories):
    products: List[GetProducts]

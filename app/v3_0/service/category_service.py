"""Service layer for model - Categories"""
from datetime import datetime

from app.dto.dto_classes import ResponseDTO
from app.utility.app_utility import check_if_company_and_branch_exist, get_value
from app.v2_0.POS.domain.models.categories import Categories
from app.v2_0.POS.domain.models.product_variants import ProductVariants
from app.v2_0.POS.domain.models.products import Products
from app.v3_0.schemas.category_schemas import AddCategory, UpdateCategory, GetCategoriesWithProducts, GetCategories
from app.v3_0.schemas.form_schema import DynamicForm
from app.v3_0.schemas.product_schemas import GetProducts
from app.v3_0.schemas.variant_schemas import GetVariants
from app.v3_0.service.tasks_services import map_to_model


def add_category(category: DynamicForm, company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            new_category = AddCategory(
                **map_to_model(category, {"company_id": company_id, "branch_id": branch_id}, Categories()))
            new_category_data = Categories(**new_category.model_dump())
            db.add(new_category_data)
            db.commit()

            return ResponseDTO(200, "Category added!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
    finally:
        db.close()


def modify_category(category: UpdateCategory, cat_id, company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            category_query = db.query(Categories).filter(Categories.category_id == cat_id)
            category_query.update(
                {"modified_on": datetime.now(), "modified_by": user_id, "name": get_value("name", category),
                 "description": get_value("description", category)})
            db.commit()

            return ResponseDTO(200, "Category updated!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
    finally:
        db.close()


def remove_category(cat_id, company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            db.query(Categories).filter(Categories.category_id == cat_id).delete()
            db.commit()

            return ResponseDTO(200, "Category deleted!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
    finally:
        db.close()


def get_variants(product_id, db):
    variants = db.query(ProductVariants).filter(ProductVariants.product_id == product_id).all()
    result = [GetVariants(variant_id=variant.variant_id, variant_name=variant.variant_name,
                          measuring_qty=variant.measuring_qty,
                          unit=variant.unit.name.title(), price=variant.price)
              for variant in variants
              ]
    return result


def get_products(category_id, db):
    products = db.query(Products).filter(Products.category_id == category_id).all()
    result = [
        GetProducts(product_name=product.product_name, description=product.description, product_id=product.product_id,
                    variants=get_variants(product.product_id, db))
        for product in products
    ]

    return result


def fetch_category_with_products(requirement, company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            categories = db.query(Categories).filter(Categories.company_id == company_id).all()
            if requirement.are_products_required is True:
                result = [GetCategoriesWithProducts(name=category.name, description=category.description,
                                                    category_id=category.category_id,
                                                    products=get_products(category.category_id, db))
                          for category in categories
                          ]

                return ResponseDTO(200, "Categories and products fetched!", result)
            result = [GetCategories(name=category.name, description=category.description,
                                    category_id=category.category_id)
                      for category in categories
                      ]

            return ResponseDTO(200, "Categories fetched!", result)
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
    finally:
        db.close()

"""Service layer for model - Categories"""
from datetime import datetime

from app.v2_0.HRMS.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.POS.domain.models.categories import Categories
from app.v2_0.POS.domain.models.product_variants import ProductVariants
from app.v2_0.POS.domain.models.products import Products
from app.v2_0.POS.domain.schemas.category_schemas import AddCategory, UpdateCategory, GetCategoriesWithProducts, \
    GetCategories
from app.v2_0.POS.domain.schemas.product_schemas import GetProducts
from app.v2_0.POS.domain.schemas.variant_schemas import GetVariants
from app.v2_0.dto.dto_classes import ResponseDTO


def add_category(category: AddCategory, company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            category.company_id = company_id
            category.branch_id = branch_id
            new_category = Categories(**category.model_dump())
            db.add(new_category)
            db.commit()

            return ResponseDTO(200, "Category added!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def modify_category(category: UpdateCategory, cat_id, company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            category_query = db.query(Categories).filter(Categories.category_id == cat_id)
            category.modified_on = datetime.now()
            category.modified_by = user_id
            category_query.update(category.model_dump())
            db.commit()

            return ResponseDTO(200, "Category updated!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


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


def get_variants(product_id, db):
    variants = db.query(ProductVariants).filter(ProductVariants.product_id == product_id).all()
    result = [GetVariants(variant_id=variant.variant_id, variant_name=variant.variant_name, quantity=variant.quantity,
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

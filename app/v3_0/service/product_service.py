"""Service layer for model - Products"""
from datetime import datetime

from app.enums.unit_enum import Unit
from app.utility.app_utility import check_if_company_and_branch_exist, get_value
from app.v2_0.POS.domain.models.product_variants import ProductVariants
from app.v2_0.POS.domain.models.products import Products
from app.dto.dto_classes import ResponseDTO
from app.v3_0.schemas.form_schema import DynamicForm
from app.v3_0.schemas.variant_schemas import AddVariant


def add_product(product: DynamicForm, company_id, branch_id, user_id, db):
    # try:
    check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

    if check is None:
        # if product.category_id is None:
        #     return ResponseDTO(204, "Category not found!", {})
        new_product = Products(product_name=get_value("product_name", product), image=get_value("image", product),
                               description=get_value("description", product),
                               category_id=get_value("category_id", product), company_id=company_id,
                               branch_id=branch_id)
        db.add(new_product)
        db.flush()

        # Adds the variant in ProductVariants table
        new_variant = ProductVariants(variant_name=get_value("product_name", product)
                                                   + " " + get_value("measuring_qty", product)
                                                   + " " + get_value("unit", product).title(),
                                      measuring_qty=get_value("measuring_qty", product),
                                      stock_qty=get_value("stock_qty", product), price=get_value("price", product),
                                      unit=Unit[get_value("unit", product)], product_id=new_product.product_id,
                                      category_id=get_value("category_id", product),
                                      company_id=company_id, branch_id=branch_id)
        db.add(new_variant)
        db.commit()

        return ResponseDTO(200, "Product added!", {})
    else:
        return check


# except Exception as exc:
#     db.rollback()
#     return ResponseDTO(204, str(exc), {})


def update_variant_name(product_name, prod_id, db):
    variants = db.query(ProductVariants).filter(ProductVariants.product_id == prod_id).all()

    for variant in variants:
        variant_name = product_name + " " + variant.measuring_qty + " " + variant.unit.name.title()
        db.query(ProductVariants).filter(ProductVariants.variant_id == variant.variant_id).update(
            {"variant_name": variant_name})


def modify_product(product: DynamicForm, prod_id, company_id, branch_id, user_id, db):
    try:
        flag = True
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            product_query = db.query(Products).filter(Products.product_id == prod_id)
            existing_product = product_query.first()

            if existing_product.product_name != product.product_name:
                flag = False

            product.modified_on = datetime.now()
            product.modified_by = user_id
            product_query.update(product.model_dump())

            if flag is False:
                update_variant_name(product.product_name, prod_id, db)

            db.commit()

            return ResponseDTO(200, "Product updated!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def remove_product(prod_id, company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            del_query = ProductVariants.__table__.delete().where(ProductVariants.product_id == prod_id)
            db.execute(del_query)
            db.query(Products).filter(Products.product_id == prod_id).delete()
            db.commit()

            return ResponseDTO(200, "Product and its variants deleted!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

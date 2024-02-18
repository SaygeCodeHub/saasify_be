"""Service layer for model - ProductVariants"""
from datetime import datetime

from app.v2_0.HRMS.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.POS.domain.models.product_variants import ProductVariants
from app.v2_0.POS.domain.models.products import Products
from app.v2_0.POS.domain.schemas.variant_schemas import UpdateVariant
from app.v2_0.dto.dto_classes import ResponseDTO


def add_variant(variant, company_id, branch_id, user_id, flag, db):
    check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

    if check is None:
        if flag is False:
            product = db.query(Products).filter(Products.product_id == variant.product_id).first()
            variant.variant_name = product.product_name + " " + variant.measuring_qty + " " + variant.unit.name.title()

        variant.company_id = company_id
        variant.branch_id = branch_id
        new_variant = ProductVariants(variant_name=variant.variant_name, measuring_qty=variant.measuring_qty,
                                      stock_qty=variant.stock_qty, price=variant.price,
                                      unit=variant.unit, product_id=variant.product_id, category_id=variant.category_id,
                                      company_id=company_id, branch_id=branch_id)
        db.add(new_variant)
        db.commit()

        return ResponseDTO(200, "Variant added!", {})
    else:
        return check


def modify_variant(variant: UpdateVariant, var_id, company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            variant_query = db.query(ProductVariants).filter(ProductVariants.variant_id == var_id)
            variant_query.update(
                {"modified_by": user_id, "modified_on": datetime.now(), "variant_name": variant.variant_name,
                 "measuring_qty": variant.measuring_qty, "stock_qty": variant.stock_qty, "price": variant.price,
                 "unit": variant.unit})
            db.commit()

            return ResponseDTO(200, "Variant updated!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def remove_variant(var_id, company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            db.query(ProductVariants).filter(ProductVariants.variant_id == var_id).delete()
            db.commit()

            return ResponseDTO(200, "Variant deleted!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

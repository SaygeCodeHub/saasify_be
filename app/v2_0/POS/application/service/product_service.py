"""Service layer for model - Products"""
from datetime import datetime

from app.v2_0.HRMS.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.POS.application.service.variant_service import add_variant
from app.v2_0.POS.domain.models.product_variants import ProductVariants
from app.v2_0.POS.domain.models.products import Products
from app.v2_0.POS.domain.schemas.product_schemas import AddProduct, UpdateProduct
from app.v2_0.POS.domain.schemas.variant_schemas import AddVariant
from app.v2_0.dto.dto_classes import ResponseDTO


def add_product(product: AddProduct, company_id, branch_id, user_id, db):
    # try:
    check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

    if check is None:
        new_product = Products(product_name=product.product_name, image=product.image, description=product.description,
                               category_id=product.category_id, company_id=company_id, branch_id=branch_id)
        db.add(new_product)
        db.flush()

        # Adds the variant in ProductVariants table
        variant = AddVariant
        variant.variant_name = product.product_name + " " + product.quantity + " " + product.unit.name.title()
        variant.price = product.price
        variant.quantity = product.quantity
        variant.unit = product.unit
        variant.category_id = product.category_id
        variant.product_id = new_product.product_id
        add_variant(variant, company_id, branch_id, user_id, True, db)
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
        variant_name = product_name + " " + variant.quantity + " " + variant.unit.name.title()
        db.query(ProductVariants).filter(ProductVariants.variant_id == variant.variant_id).update(
            {"variant_name": variant_name})


def modify_product(product: UpdateProduct, prod_id, company_id, branch_id, user_id, db):
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

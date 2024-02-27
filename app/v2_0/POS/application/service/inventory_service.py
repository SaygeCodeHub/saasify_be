"""Service layer for Inventory operations"""
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.POS.domain.models.product_variants import ProductVariants
from app.v2_0.POS.domain.schemas.inventory_schemas import GetAllInventory
from app.dto.dto_classes import ResponseDTO


def fetch_all_inventory(company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            variants = db.query(ProductVariants).filter(ProductVariants.company_id == company_id).all()
            result = [
                GetAllInventory(variant_name=variant.variant_name, measuring_qty=variant.measuring_qty,
                                stock_qty=variant.stock_qty, unit=variant.unit.name.title(), price=variant.price,
                                product_id=variant.product_id)
                for variant in variants
            ]

            return ResponseDTO(200, "Inventory fetched!", result)
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

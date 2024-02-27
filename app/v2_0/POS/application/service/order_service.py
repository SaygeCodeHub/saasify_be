"""Service layer for model -Orders"""
from app.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.POS.domain.models.orders import Orders
from app.dto.dto_classes import ResponseDTO


def place_new_order(order, company_id, branch_id, user_id, db):
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            order.placed_by = user_id
            new_order = Orders(**order.model_dump())
            db.add(new_order)
            db.commit()
            return ResponseDTO(200, "Order placed!", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})

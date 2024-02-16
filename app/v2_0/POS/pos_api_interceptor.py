from fastapi import APIRouter, Depends

from app.v2_0.POS.application.service.category_service import add_category, modify_category, remove_category, \
    fetch_category_with_products
from app.v2_0.POS.application.service.inventory_service import fetch_all_inventory
from app.v2_0.POS.application.service.order_service import place_new_order
from app.v2_0.POS.application.service.product_service import add_product, modify_product, remove_product
from app.v2_0.POS.application.service.variant_service import add_variant, modify_variant, remove_variant
from app.v2_0.POS.domain.schemas.category_schemas import AddCategory, UpdateCategory, ResponseRequirements
from app.v2_0.POS.domain.schemas.order_schemas import PlaceOrder
from app.v2_0.POS.domain.schemas.product_schemas import AddProduct, UpdateProduct
from app.v2_0.POS.domain.schemas.variant_schemas import AddVariant, UpdateVariant
from app.v2_0.infrastructure.database import Base, engine, get_db

router = APIRouter()
Base.metadata.create_all(bind=engine)

"""----------------------------------------------Category related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/addCategory")
def create_category(category: AddCategory, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return add_category(category, company_id, branch_id, user_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateCategory/{cat_id}")
def update_category(category: UpdateCategory, cat_id: int, company_id: int, branch_id: int, user_id: int,
                    db=Depends(get_db)):
    return modify_category(category, cat_id, company_id, branch_id, user_id, db)


@router.delete("/v2.0/{company_id}/{branch_id}/{user_id}/deleteCategory/{cat_id}")
def delete_category(cat_id: int, company_id: int, branch_id: int, user_id: int,
                    db=Depends(get_db)):
    return remove_category(cat_id, company_id, branch_id, user_id, db)


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getCategoryWithProduct")
def get_category_with_products(requirement: ResponseRequirements, company_id: int, branch_id: int, user_id: int,
                               db=Depends(get_db)):
    return fetch_category_with_products(requirement, company_id, branch_id, user_id, db)


"""----------------------------------------------Product related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/addProduct")
def create_product(product: AddProduct, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return add_product(product, company_id, branch_id, user_id, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateProduct/{prod_id}")
def update_product(product: UpdateProduct, prod_id: int, company_id: int, branch_id: int, user_id: int,
                   db=Depends(get_db)):
    return modify_product(product, prod_id, company_id, branch_id, user_id, db)


@router.delete("/v2.0/{company_id}/{branch_id}/{user_id}/deleteProduct/{prod_id}")
def delete_product(prod_id: int, company_id: int, branch_id: int, user_id: int,
                   db=Depends(get_db)):
    return remove_product(prod_id, company_id, branch_id, user_id, db)


"""----------------------------------------------Variant related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/addVariant")
def create_variant(variant: AddVariant, company_id: int, branch_id: int, user_id: int, flag=False, db=Depends(get_db)):
    return add_variant(variant, company_id, branch_id, user_id, flag, db)


@router.put("/v2.0/{company_id}/{branch_id}/{user_id}/updateVariant/{var_id}")
def update_variant(variant: UpdateVariant, var_id: int, company_id: int, branch_id: int, user_id: int,
                   db=Depends(get_db)):
    return modify_variant(variant, var_id, company_id, branch_id, user_id, db)


@router.delete("/v2.0/{company_id}/{branch_id}/{user_id}/deleteVariant/{var_id}")
def delete_variant(var_id: int, company_id: int, branch_id: int, user_id: int,
                   db=Depends(get_db)):
    return remove_variant(var_id, company_id, branch_id, user_id, db)


"""----------------------------------------------Order related APIs-------------------------------------------------------------------"""


@router.post("/v2.0/{company_id}/{branch_id}/{user_id}/placeOrder")
def place_order(order: PlaceOrder, company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return place_new_order(order, company_id, branch_id, user_id, db)


"""----------------------------------------------Inventory related APIs-------------------------------------------------------------------"""


@router.get("/v2.0/{company_id}/{branch_id}/{user_id}/getAllInventory")
def get_all_inventory(company_id: int, branch_id: int, user_id: int, db=Depends(get_db)):
    return fetch_all_inventory(company_id, branch_id, user_id, db)

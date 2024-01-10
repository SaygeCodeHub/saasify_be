from typing import List

from fastapi import APIRouter, Depends
	@@ -6,14 +7,15 @@
from app import schemas
from app.database import get_db, engine
from app.v1_1 import models
from app.v1_1.schema import AddCustomer

router = APIRouter()
models.Base.metadata.create_all(bind=engine)


@router.post('/v1.1/authenticateUser')
def create_user_v1_1(authentication: schemas.Authentication, db: Session = Depends(get_db)):
    try:
        user_exists = db.query(models.UsersV).get(
            authentication.user_id)
	@@ -22,7 +24,7 @@ def create_user_v1_1(authentication: schemas.Authentication, db: Session = Depen
            try:
                add_new_user_v1_1(authentication, db)
            except Exception:
                return {"status": 204, "message": "User is NOT registered, please sing up",
                        "data": {"user": {}, "companies": []}}

        company_user_data = db.query(models.UserCompanyV).filter(
	@@ -95,36 +97,52 @@ def add_new_user_v1_1(authentication, db):
    db.commit()
    db.refresh(new_user_data)

    return {"status": 200, "message": "User successfully Authenticated",
            "data": {"user": new_user_data, "companies": []}}


@router.post('/v1.1/{userId}/addCompany')
def create_company_v1_1(company: schemas.CreateCompany, userId: str, db: Session = Depends(get_db)):
    try:
        user_exists = db.query(models.UsersV).filter(models.UsersV.user_id == userId).first()

        if user_exists:
            try:
                company.owner = userId
                new_company = models.CompaniesV(company_name=company.company_name,
                                                company_domain=company.company_domain, owner=company.owner)
                db.add(new_company)
                db.commit()
                db.refresh(new_company)
                user_company = models.UserCompanyV(user_id=userId, company_id=new_company.company_id)
                db.add(user_company)
                db.commit()
                new_branch = models.Branches(branch_name=company.branch_name,
                                             branch_contact=company.branch_contact,
                                             branch_currency=company.branch_currency,
                                             branch_active=company.branch_active,
                                             branch_address=company.branch_address)
                db.add(new_branch)
                return {"status": 200, "message": "Company added successfully", "data": {}}

            except Exception:
                return {"status": 204, "message": "Something when wrong", "data": {}}

        return {"status": 204, "message": "User doesn't exist", "data": user_exists}

	@@ -140,6 +158,8 @@ def create_branch_v1_1(createBranch: schemas.Branch, companyId: str, userId: str
            company = db.query(models.CompaniesV).get(companyId)
            if company:
                createBranch.company_id = companyId
                new_branch = models.Branches(**createBranch.model_dump())
                db.add(new_branch)
                db.commit()
	@@ -450,7 +470,7 @@ def get_add_categories(companyId: str, userId: str, branchId: str, db=Depends(ge
            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:
                response_data = []
                categories = db.query(models.Category).filter(models.Category.is_active == True).order_by(
                    asc(models.Category.category_id)).all()
                for category in categories:
                    category_data = {
	@@ -469,8 +489,8 @@ def get_add_categories(companyId: str, userId: str, branchId: str, db=Depends(ge

                        variants = db.query(models.Variants).filter(
                            models.Variants.product_id == product.product_id).filter(
                            models.Variants.draft == False).filter(
                            models.Variants.is_active == True).all()
                        if variants:
                            print("if variants")
                            product_data = {
	@@ -793,11 +813,12 @@ def book_order(bookOrder: schemas.BookOrder, companyId: str, userId: str, branch
                                        "CGST": variant.CGST if variant.CGST else 0.0,
                                        "count": count}
                                order_items.append(item)
                                stock_update = db.query(models.Inventory).filter(
                                    models.Inventory.stock_id == variant.stock_id).first()
                                stock_update.update(branch_id=branchId, company_id=companyId,
                                                    stock=stock_data.stock - count,
                                                    variant_id=variant_id)

                                db.commit()

	@@ -907,7 +928,8 @@ def add_category(addCategory: schemas.Categories, companyId: str, userId: str, b
                else:
                    category_added = models.Category(branch_id=branchId, company_id=companyId,
                                                     category_name=addCategory.category_name,
                                                     is_active=addCategory.is_active)
                    db.add(category_added)
                    db.commit()

	@@ -932,9 +954,9 @@ def edit_category(editCategory: schemas.Categories, companyId: str, userId: str,

                branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
                if branch:

                    category = db.query(models.Category).filter(
                        models.Category.category_id == editCategory.category_id).first()
                    category_name_exists = db.query(models.Category).filter(
                        models.Category.category_name == editCategory.category_name).filter(
                        models.Category.category_id != editCategory.category_id).first()
	@@ -944,9 +966,9 @@ def edit_category(editCategory: schemas.Categories, companyId: str, userId: str,
                                    "message": f"Category with {editCategory.category_name} already exists"}

                        else:
                            category.update(branch_id=branchId, company_id=companyId,
                                            category_name=editCategory.category_name,
                                            is_active=editCategory.is_active)
                            db.commit()
                            return {"status": 200, "data": {}, "message": "Successfully"}

	@@ -1078,15 +1100,14 @@ def edit_branch(companyId: str, userId: str, editBranch: schemas.Branch, db=Depe
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            branch = db.query(models.Branches).filter(
                models.Branches.branch_id == editBranch.branch_id).first()
            if branch:
                branch.update(
                    branch_name=editBranch.branch_name,
                    branch_contact=editBranch.branch_contact,
                    branch_address=editBranch.branch_address,
                    branch_currency=editBranch.branch_currency,
                    branch_active=editBranch.branch_active)

                db.commit()
                return {"status": 200, "data": {}, "message": "Successfully"}
	@@ -1102,7 +1123,7 @@ def edit_branch(companyId: str, userId: str, editBranch: schemas.Branch, db=Depe


@router.post('/v1.1/{userId}/{companyId}/{branchId}/addPaymentMethod')
def add_category(addPaymentType: schemas.Payment, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
	@@ -1118,6 +1139,9 @@ def add_category(addPaymentType: schemas.Payment, companyId: str, userId: str, b
                            "message": f"Payment Method with {addPaymentType.category_name} already exists"}

                else:
                    payment_added = models.PaymentMethod(**addPaymentType.model_dump())
                    db.add(payment_added)
                    db.commit()
	@@ -1134,7 +1158,7 @@ def add_category(addPaymentType: schemas.Payment, companyId: str, userId: str, b


@router.put('/v1.1/{userId}/{companyId}/{branchId}/editPaymentMethod')
def edit_category(editPayment: schemas.Payment, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
	@@ -1143,8 +1167,9 @@ def edit_category(editPayment: schemas.Payment, companyId: str, userId: str, bra
            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:

                payment = db.query(models.PaymentMethod).filter(
                    models.PaymentMethod.payment_id == editPayment.payment_id).first()
                payment_method_exists = db.query(models.PaymentMethod).filter(
                    models.PaymentMethod.payment_name == editPayment.payment_name).filter(
                    models.PaymentMethod.payment_id != editPayment.payment_id).first()
	@@ -1154,9 +1179,11 @@ def edit_category(editPayment: schemas.Payment, companyId: str, userId: str, bra
                                "message": f"Payment with {editPayment.payment_name} already exists"}

                    else:
                        payment.update(branch_id=branchId, company_id=companyId,
                                       payment_name=editPayment.payment_name,
                                       is_active=editPayment.is_active)

                    db.commit()
                    return {"status": 200, "data": {}, "message": "Successfully"}
	@@ -1231,9 +1258,17 @@ def get_all_payment_methods(companyId: str, userId: str, branchId: str, db=Depen
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.post('/v1.1/addCustomer')
def create_customer(customer: AddCustomer, db=Depends(get_db)):
    """Adds a new customer"""
    new_customer = models.Customer(**customer.model_dump())
    db.add(new_customer)
    db.commit()
	@@ -1242,35 +1277,37 @@ def create_customer(customer: AddCustomer, db=Depends(get_db)):
    return {"status": 200, "data": {new_customer}, "message": "Customer created successfully"}


@router.get("/v1.1/getCustomers", response_model=List[AddCustomer])
def get_customers(db=Depends(get_db)):
    """Gets all the customers"""
    customers = db.query(models.Customer).all()

    return {"status": 200, "data": {customers}, "message": "Existing customers"}


@router.get("/v1.1/getCustomer/{customer_id}", response_model=AddCustomer)
def get_by_id(customer_id: int, db=Depends(get_db)):
    """Gets a customer by id"""
    customer_by_id = db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()

    if customer_by_id is None:
        return {"status": 204, "data": {}, "message": f"Customer with id {customer_id} doesnt exist"}

    return {"status": 200, "data": {customer_by_id}, "message": f"Customer by id {customer_id}"}


@router.put("/v1.1/updateCustomer/{customer_id}")
def update_customer(customer_id: int, incoming_customer_data: AddCustomer, db=Depends(get_db)):
    """Updates the customer"""
    customer_query = db.db.query(models.Customer).filter(models.Customer.customer_id == customer_id)
    to_be_updated_customer = customer_query.first()

    if to_be_updated_customer is None:
        return {"status": 204, "data": {}, "message": f"Customer with id {customer_id} doesnt exist"}

    updated_customer = customer_query.update(**incoming_customer_data.model_dump())
    db.commit()

    return {"status": 200, "data": {updated_customer}, "message": "Customer updated successfully."}

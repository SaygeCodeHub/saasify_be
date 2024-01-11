from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import and_, asc, desc, func
from sqlalchemy.orm import Session
from app import schemas
from app.database import get_db, engine
from app.v1_1 import models
from app.v1_1.schema import UpdateCustomer, AddCustomer

router = APIRouter()
models.Base.metadata.create_all(bind=engine)


@router.post('/v1.1/authenticateUser')
def create_user_v1_1(authentication: schemas.Authentication, db: Session = Depends(get_db)):
    """Add Comment here"""
    try:
        user_exists = db.query(models.UsersV).get(
            authentication.user_id)
        companies = []
        if not user_exists:
            try:
                add_new_user_v1_1(authentication, db)
            except Exception:
                return {"status": 204, "message": "User is NOT registered, please sign up",
                        "data": {"user": {}, "companies": []}}

        company_user_data = db.query(models.UserCompanyV).filter(
            models.UserCompanyV.user_id == authentication.user_id).all()
        company_list(company_user_data, db, authentication.user_id, companies)

        if authentication.user_name == "":
            return {"status": 200, "message": "User successfully Authenticated",
                    "data": {"user": {"user_name": user_exists.user_name, "user_id": user_exists.user_id,
                                      "user_contact": user_exists.user_contact}, "companies": companies}}

        else:
            update = db.query(models.UsersV).filter(models.UsersV.user_id == authentication.user_id).update({
                "user_name": authentication.user_name})
            db.query(update)
            db.commit()

            user_update = db.query(models.UsersV).get(authentication.user_id)
            return {"status": 200, "message": "User successfully Authenticated",
                    "data": {"user": user_update, "companies": companies}}
    except Exception as e:
        print(e)
        return {"status": 500, "message": e, "data": {"user": {}, "companies": []}}


def company_list(company_user_data, db, user_id, companies):
    for company in company_user_data:
        company_data = db.query(models.CompaniesV).filter(
            and_(models.CompaniesV.company_id == models.CompaniesV.company_id,
                 models.CompaniesV.company_id == company.company_id)).first()
        owner = True if company_data.owner == user_id else False

        companies.append({
            "company_id": company_data.company_id,
            "company_domain": company_data.company_domain if company_data.company_domain is not None else "",
            "company_email": company_data.company_email if company_data.company_email is not None else "",
            "company_name": company_data.company_name if company_data.company_name is not None else "",
            "services": company_data.services if company_data.services is not None else "",
            "company_logo": company_data.company_logo if company_data.company_logo is not None else "",
            "onboarding_date": company_data.onboarding_date,
            "is_owner": owner,
            "role": [0] if company_data.owner == user_id else [1],
            "branches": branch_list(True if company_data.owner == user_id else False, company_data.company_id, db)})

        return companies


def branch_list(owner: bool, companyId=str, db=Depends(get_db)):
    branches = db.query(models.Branches).filter(models.Branches.company_id == companyId).order_by(
        asc(models.Branches.branch_id)).all()
    branch_dicts = []
    for branch in branches:
        branch_dicts.append({
            "branch_id": branch.branch_id,
            "branch_name": branch.branch_name,
            "branch_contact": branch.branch_contact,
            "branch_currency": branch.branch_currency,
            "branch_active": branch.branch_active,
            "branch_address": branch.branch_address,
            "role": [0] if owner else [1]
        })

    return branch_dicts


def add_new_user_v1_1(authentication, db):
    new_user_data = models.UsersV(
        **authentication.model_dump())
    db.add(new_user_data)
    db.commit()
    db.refresh(new_user_data)

    return {"status": 200, "message": "User created successfully",
            "data": {"user": new_user_data, "companies": []}}


def add_init_branch(company, db):
    """After creation of any company, this method will add a branch to it. """
    new_branch = models.Branches(company_id=company.company_id,
                                 branch_name=company.branch_name,
                                 branch_contact=company.branch_contact,
                                 branch_currency=company.branch_currency,
                                 branch_active=company.branch_active,
                                 branch_address=company.branch_address,
                                 modified_by=company.owner,
                                 modified_on=datetime.now())
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)


@router.post('/v1.1/{userId}/addCompany')
def create_company_v1_1(company: schemas.CreateCompany, userId: str, db: Session = Depends(get_db)):
    """Creates a company and then adds a branch to it"""
    try:
        user_exists = db.query(models.UsersV).filter(models.UsersV.user_id == userId).first()

        if user_exists:
            try:
                company.owner = userId
                new_company = models.CompaniesV(company_name=company.company_name,
                                                company_domain=company.company_domain, modified_by=company.owner,
                                                modified_on=datetime.now(),
                                                owner=company.owner)
                db.add(new_company)
                db.commit()
                db.refresh(new_company)
                user_company = models.UserCompanyV(user_id=userId, company_id=new_company.company_id)
                db.add(user_company)
                db.commit()
                company.company_id = new_company.company_id

                add_init_branch(company, db)

                return {"status": 200, "message": "Company added successfully", "data": {}}

            except Exception as exc:
                return exc

        return {"status": 204, "message": "User doesn't exist", "data": user_exists}

    except Exception as e:
        return {"status": 500, "message": e, "data": {}}


@router.post('/v1.1/{userId}/{companyId}/addBranch')
def create_branch_v1_1(createBranch: schemas.Branch, companyId: str, userId: str, db=Depends(get_db)):
    try:
        user = db.query(models.UsersV).get(userId)
        if user:
            company = db.query(models.CompaniesV).get(companyId)
            if company:
                createBranch.company_id = companyId
                createBranch.modified_by = userId
                createBranch.modified_on = datetime.now()
                new_branch = models.Branches(**createBranch.model_dump())
                db.add(new_branch)
                db.commit()
                return {"status": 200, "message": "branch added successfully", "data": {}}
            else:
                return {"status": 204, "message": "Company doesn't exist", "data": {}}

        else:
            return {"status": 204, "message": "Un Authorized", "data": {}}
    except Exception as e:
        return {"status": 204, "message": e, "data": {}}


@router.post('/v1.1/{userId}/{companyId}/{branchId}/addProduct')
def add_product(createProduct: schemas.AddProducts, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:

            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:
                category = db.query(models.Category).filter(
                    models.Category.category_name == createProduct.category_name).first()
                if category:
                    category_id = category.category_id
                else:
                    new_category = models.Category(branch_id=branchId, company_id=companyId,
                                                   category_name=createProduct.category_name)
                    category_id = new_category.category_id
                    db.add(new_category)
                    db.commit()

                if createProduct.brand_name is not None:

                    brand = db.query(models.Brand).filter(
                        models.Brand.brand_name == createProduct.brand_name).first()
                    if brand:
                        brand_id = brand.brand_id
                    else:
                        new_brand = models.Brand(branch_id=branchId, company_id=companyId,
                                                 brand_name=createProduct.brand_name)
                        brand_id = new_brand.brand_id
                        db.add(new_brand)

                        db.commit()
                else:
                    brand_id = None

                if createProduct.product_id:
                    product_check = db.query(models.Products).filter(
                        models.Products.product_id == createProduct.product_id).first()
                    if product_check:
                        product_id = createProduct.product_id
                    else:
                        product_id = None
                else:
                    if brand_id is not None:
                        product = db.query(models.Products).filter(
                            models.Products.category_id == category_id).filter(
                            models.Products.brand_id == brand_id).filter(
                            models.Products.product_name == createProduct.product_name).first()
                    else:
                        product = db.query(models.Products).filter(
                            models.Products.category_id == category_id).filter(
                            models.Products.product_name == createProduct.product_name).first()
                    if product:
                        product_id = product.product_id
                    else:
                        new_product = models.Products(branch_id=branchId, company_id=companyId, category_id=category_id,
                                                      brand_id=brand_id, product_name=createProduct.product_name,
                                                      product_description=createProduct.product_description)

                        product_id = new_product.product_id
                        db.add(new_product)
                        db.commit()

                if createProduct.barcode:

                    variant = db.query(models.Variants).filter(
                        models.Variants.barcode == createProduct.barcode).first()
                    if variant:
                        return {"status": 204, "data": {}, "message": "variant already exists"}
                    else:
                        if createProduct.stock:
                            new_stock = models.Inventory(branch_id=branchId, company_id=companyId,
                                                         stock=createProduct.stock)
                            db.add(new_stock)
                            db.flush()
                            new_variant = models.Variants(branch_id=branchId, company_id=companyId,
                                                          product_id=product_id,
                                                          cost=createProduct.cost,
                                                          quantity=createProduct.quantity,
                                                          unit=createProduct.unit,
                                                          discount_percent=createProduct.discount_percent,
                                                          images=createProduct.images,
                                                          draft=createProduct.draft,
                                                          is_active=createProduct.variant_active,
                                                          barcode=createProduct.barcode,
                                                          SGST=createProduct.SGST,
                                                          CGST=createProduct.CGST,
                                                          stock_id=new_stock.stock_id,
                                                          restock_reminder=createProduct.restock_reminder)
                            db.add(new_variant)
                            db.flush()
                            new_stock.variant_id = new_variant.variant_id
                            db.commit()
                            return {"status": 200, "data": {"category_name": createProduct.category_name,
                                                            "brand_name": createProduct.brand_name,
                                                            "product_name": createProduct.product_name,
                                                            "product_id": product_id,
                                                            "product_description": createProduct.product_description},
                                    "message": "Product Added successfully"}
                        else:
                            new_variant = models.Variants(branch_id=branchId,
                                                          company_id=companyId,
                                                          product_id=product_id,
                                                          cost=createProduct.cost,
                                                          quantity=createProduct.quantity,
                                                          unit=createProduct.unit,
                                                          stock_id=None,
                                                          discount_percent=createProduct.discount_percent,
                                                          images=createProduct.images,
                                                          draft=createProduct.draft,
                                                          is_active=createProduct.is_active,
                                                          barcode=createProduct.barcode,
                                                          SGST=createProduct.SGST,
                                                          CGST=createProduct.CGST,
                                                          restock_reminder=createProduct.restock_reminder)
                            db.add(new_variant)
                            db.commit()
                            return {"status": 200, "data": {"category_name": createProduct.category_name,
                                                            "brand_name": createProduct.brand_name,
                                                            "product_name": createProduct.product_name,
                                                            "product_id": product_id,
                                                            "product_description": createProduct.product_description},
                                    "message": "Product Added successfully"}
                else:
                    return {"status": 200, "data": {"category_name": createProduct.category_name,
                                                    "brand_name": createProduct.brand_name,
                                                    "product_name": createProduct.product_name,
                                                    "product_id": product_id,
                                                    "product_description": createProduct.product_description},
                            "message": "Product Added successfully"}

            else:
                return {"status": 204, "data": {}, "message": "Branch doesnt exist"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.get('/v1.1/{userId}/{companyId}/{branchId}/getAllCategories')
def get_add_categories(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:
                categories = db.query(models.Category).order_by(asc(models.Category.category_id)).all()
                return schemas.GetAllCategories(status=200, data=categories, message="get all categories")
            else:
                return schemas.GetAllCategories(status=204, data=[], message="Branch doesnt exist")

        else:
            return schemas.GetAllCategories(status=204, data=[], message="Company doesnt exist")

    else:
        return schemas.GetAllCategories(status=204, data=[], message="User doesnt exist")


@router.get('/v1.1/{userId}/{companyId}/{branchId}/getAllProducts')
def get_add_categories(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:
                products_list = db.query(models.Products).order_by(asc(models.Products.product_id)).all()
                products_data = []
                for product in products_list:
                    category = db.query(models.Category).filter(
                        models.Category.category_id == product.category_id).first()
                    brand = db.query(models.Brand).filter(models.Brand.brand_id == product.brand_id).first()
                    variants = db.query(models.Variants).filter(
                        models.Variants.product_id == product.product_id).all()

                    if brand:
                        brand_name = brand.brand_name
                    else:
                        brand_name = None

                    for variant in variants:
                        if variant.stock_id:
                            stock = db.query(models.Inventory).filter(
                                models.Inventory.stock_id == variant.stock_id).first()
                            stock_count = stock.stock
                        else:
                            stock_count = 0

                        products_data.append({
                            "category_id": category.category_id,
                            "category_name": category.category_name,
                            "category_active": category.is_active,
                            "product_id": product.product_id,
                            "product_name": product.product_name,
                            "brand_name": brand_name,
                            "brand_id": product.brand_id,
                            "variant_id": variant.variant_id,
                            "cost": variant.cost if variant.cost is not None else 0.0,
                            "quantity": variant.quantity,
                            "discount_percent": variant.discount_percent if variant.discount_percent is not None else 0.0,
                            "stock": stock_count,
                            "stock_id": variant.stock_id,
                            "product_description": product.product_description,
                            "images": variant.images,
                            "unit": variant.unit,
                            "variant_active": variant.is_active,
                            "barcode": variant.barcode, "draft": variant.draft,
                            "restock_reminder": variant.restock_reminder,
                            "SGST": variant.SGST if variant.SGST else 0.0,
                            "CGST": variant.CGST if variant.CGST else 0.0,
                            "currency": branch.branch_currency})

                return {"status": 200, "data": products_data, "message": "get all products"}

            else:
                return {"status": 204, "data": [], "message": "Branch  doesn't exist"}

        else:
            return {"status": 204, "data": [], "message": "Company does not exists"}

    else:
        return {"status": 204, "data": [], "message": "User does not exists"}


@router.get('/v1.1/{userId}/{companyId}/{branchId}/getInventoryProducts')
def get_add_categories(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:

            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:

                variants = db.query(models.Variants).order_by(asc(models.Variants.variant_id)).all()
                products = []
                for variant in variants:
                    product = db.query(models.Products).filter(
                        models.Products.product_id == variant.product_id).first()
                    category = db.query(models.Category).filter(
                        models.Category.category_id == product.category_id).first()
                    brand = db.query(models.Brand).filter(models.Brand.brand_id == product.brand_id).first()
                    if brand:
                        brand_name = brand.brand_name
                    else:
                        brand_name = None

                    if variant.stock_id is None:
                        stock_count = 0
                    else:
                        stock = db.query(models.Inventory).filter(
                            models.Inventory.stock_id == variant.stock_id).first()
                        stock_count = stock.stock
                    if not variant.draft:
                        products.append({
                            "category_id": category.category_id,
                            "category_name": category.category_name,
                            "product_id": variant.product_id,
                            "product_name": product.product_name,
                            "brand_name": brand_name,
                            "brand_id": product.brand_id,
                            "variant_id": variant.variant_id,
                            "cost": variant.cost,
                            "quantity": variant.quantity,
                            "discount_percent": variant.discount_percent,
                            "stock": stock_count,
                            "stock_id": variant.stock_id,
                            "product_description": product.product_description,
                            "images": variant.images,
                            "unit": variant.unit,
                            "barcode": variant.barcode, "draft": variant.draft,
                            "currency": branch.branch_currency,
                            "SGST": variant.SGST if variant.SGST else 0.0,
                            "CGST": variant.CGST if variant.CGST else 0.0,
                            "restock_reminder": variant.restock_reminder})

                return {"status": 200, "data": products, "message": "get all products"}
        else:
            return {"status": 204, "data": [], "message": "Company does not exists"}

    else:
        return {"status": 204, "data": [], "message": "User does not exists"}


@router.get('/v1.1/{userId}/{companyId}/{branchId}/getProductsByCategory')
def get_add_categories(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:
                response_data = []
                categories = db.query(models.Category).filter(models.Category.is_active is True).order_by(
                    asc(models.Category.category_id)).all()
                for category in categories:
                    category_data = {
                        "category_id": category.category_id,
                        "category_name": category.category_name,
                        "products": []
                    }
                    products = db.query(models.Products).filter(
                        models.Products.category_id == category.category_id).all()
                    for product in products:
                        brand = db.query(models.Brand).filter(models.Brand.brand_id == product.brand_id).first()
                        if brand:
                            brand_name = brand.brand_name
                        else:
                            brand_name = None

                        variants = db.query(models.Variants).filter(
                            models.Variants.product_id == product.product_id).filter(
                            models.Variants.draft is False).filter(
                            models.Variants.is_active is True).all()
                        if variants:
                            print("if variants")
                            product_data = {
                                "product_id": product.product_id,
                                "product_name": product.product_name,
                                "brand_id": product.brand_id,
                                "brand_name": brand_name,
                                "product_description": product.product_description,
                                "variants": []
                            }
                            variant_list = []
                            for variant in variants:
                                print("for variant in variants")
                                if variant.stock_id:
                                    print("if variant.stock_id")
                                    stock = db.query(models.Inventory).filter(
                                        models.Inventory.stock_id == variant.stock_id).first()
                                    if stock.stock != 0:
                                        print("stock.stock != 0")
                                        variant_list.append({
                                            "variant_id": variant.variant_id,
                                            "cost": variant.cost,
                                            "quantity": variant.quantity,
                                            "discount_percent": variant.discount_percent,
                                            "stock_id": variant.stock_id,
                                            "stock": stock.stock,
                                            "images": variant.images,
                                            "unit": variant.unit,
                                            "barcode": variant.barcode,
                                            "restock_reminder": variant.restock_reminder,
                                            "draft": variant.draft,
                                            "SGST": variant.SGST if variant.SGST else 0.0,
                                            "CGST": variant.CGST if variant.CGST else 0.0,
                                            "currency": branch.branch_currency})

                            if variant_list:
                                product_data['variants'] = variant_list
                                category_data["products"].append(product_data)

                    response_data.append(category_data)

                return {"status": 200, "data": response_data, "message": "get all products"}

        else:
            return {"status": 204, "data": [], "message": "Company does not exists"}

    else:
        return {"status": 204, "data": [], "message": "User does not exists"}


@router.put('/v1.1/{userId}/{companyId}/{branchId}/editProduct')
def edit_product(createProduct: schemas.EditProduct, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            try:
                branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
                if branch:

                    category = db.query(models.Category).filter(
                        models.Category.category_name == createProduct.category_name).first()
                    if category:
                        category_id = category.category_id
                    else:
                        category_added = models.Category(branch_id=branchId, company_id=companyId,
                                                         category_name=createProduct.category_name)
                        category_id = category_added.category_id
                        db.add(category_added)
                        db.commit()

                    if createProduct.brand_name is not None:
                        brand = db.query(models.Brand).filter(
                            models.Brand.brand_name == createProduct.brand_name).first()
                        if brand:
                            brand_id = brand.brand_id
                        else:
                            brand_added = models.Brand(branch_id=branchId, company_id=companyId,
                                                       brand_name=createProduct.brand_name)
                            brand_id = brand_added.brand_id
                            db.add(brand_added)
                            db.commit()
                    else:
                        brand_id = None

                    if createProduct.product_id:
                        product_check = db.query(models.Products).filter(
                            models.Products.product_id == createProduct.product_id).first()
                        if product_check:
                            product_id = createProduct.product_id
                            product_check.update(branch_id=branchId, company_id=companyId, category_id=category_id,
                                                 brand_id=brand_id,
                                                 product_name=createProduct.product_name,
                                                 product_description=createProduct.product_description)

                            db.commit()

                        else:
                            return {"status": 204, "data": {}, "message": "Invalid product id"}

                        if createProduct.variant_id:
                            variant = db.query(models.Variants).filter(
                                models.Variants.variant_id == createProduct.variant_id).first()
                            if variant:
                                stock_update = db.query(models.Inventory).filter(
                                    models.Inventory.stock_id == variant.stock_id).firts()
                                stock_update.update(branch_id=branchId, company_id=companyId, stock=createProduct.stock,
                                                    variant_id=variant.variant_id)

                                variant.update(branch_id=branchId, company_id=companyId, product_id=product_id,
                                               cost=createProduct.cost,
                                               stock_id=variant.stock_id,
                                               quantity=createProduct.quantity,
                                               unit=createProduct.unit,
                                               discount_percent=createProduct.discount_percent,
                                               images=createProduct.images,
                                               draft=createProduct.draft,
                                               barcode=createProduct.barcode,
                                               restock_reminder=createProduct.restock_reminder,
                                               SGST=createProduct.SGST,
                                               CGST=createProduct.CGST,
                                               is_active=createProduct.variant_active)

                                db.commit()
                                return {"status": 200, "data": {"category_name": createProduct.category_name,
                                                                "brand_name": createProduct.brand_name,
                                                                "product_name": createProduct.product_name,
                                                                "product_id": product_id,
                                                                "product_description": createProduct.product_description},
                                        "message": "Product Edited successfully"}
                            else:
                                return {"status": 204, "data": {}, "message": "invalid variant id"}
                        else:
                            variant = db.query(models.Variants).filter(
                                models.Variants.barcode == createProduct.barcode).first()
                            if variant:
                                return {"status": 204, "data": {}, "message": "variant already exists"}
                            else:
                                stock_add = models.Inventory(branch_id=branchId, company_id=companyId,
                                                             stock=createProduct.stock)
                                stock_id = stock_add.stock_id
                                variant_added = models.Variants(branch_id=branchId, company_id=companyId,
                                                                product_id=product_id,
                                                                cost=createProduct.cost,
                                                                quantity=createProduct.quantity,
                                                                unit=createProduct.unit,
                                                                stock_id=stock_id,
                                                                discount_percent=createProduct.discount_percent,
                                                                images=createProduct.images,
                                                                draft=createProduct.draft,
                                                                barcode=createProduct.barcode,
                                                                SGST=createProduct.SGST,
                                                                CGST=createProduct.CGST,
                                                                restock_reminder=createProduct.restock_reminder)
                                variant_id = variant_added.variant_id
                                stock_add.variant_id = variant_id
                                db.add(stock_add)
                                db.add(variant_added)

                                db.commit()
                                return {"status": 200, "data": {"category_name": createProduct.category_name,
                                                                "brand_name": createProduct.brand_name,
                                                                "product_name": createProduct.product_name,
                                                                "product_id": product_id,
                                                                "product_description": createProduct.product_description},
                                        "message": "Product Edited successfully"}

                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.delete('/v1.1/{userId}/{companyId}/{branchId}/deleteVariant')
def delete_products(deleteVariants: schemas.DeleteVariants, companyId: str, userId: str, branchId: str,
                    db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            try:

                branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
                if branch:
                    for variant in deleteVariants.variant_ids:
                        variant_exists = db.query(models.Variants).filter(
                            models.Variants.variant_id == variant).first()
                        if not variant_exists:
                            return {"status": 204, "data": {}, "message": f"Incorrect variant id {variant_exists}"}

                    db.query(models.Variants).filter(models.Variants.variant_id.in_(deleteVariants.variant_ids)).delete(
                        synchronize_session=False)
                    db.query(models.Variants).filter(
                        models.Inventory.variant_id.in_(deleteVariants.variant_ids)).delete(synchronize_session=False)

                    db.commit()

                    products = db.query(models.Products).all()
                    for product in products:
                        variants = db.query(models.Variants).filter(
                            models.Variants.product_id == product.product_id).all()
                        if not variants:
                            db.query(models.Products).filter(
                                models.Products.product_id.in_([product.product_id])).delete(synchronize_session=False)
                            db.commit()

                    return {"status": 200, "data": {}, "message": "variants deleted successfully"}
                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.post('/v1.1/{userId}/{companyId}/{branchId}/updateStock')
def update_stock(updateStock: schemas.UpdateStock, companyId: str, userId: str, branchId: str,
                 db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            try:
                branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
                if branch:
                    if not updateStock.stock_id:
                        return {"status": 204, "data": {}, "message": "Invalid stock Id"}
                    else:
                        stock = db.query(models.Inventory).filter(
                            models.Inventory.stock_id == updateStock.stock_id).first()
                        if not stock:
                            return {"status": 204, "data": {}, "message": "Stock id not found"}
                        else:
                            if updateStock.increment:
                                final_stock = stock.stock + updateStock.stock
                            else:
                                final_stock = stock.stock - updateStock.stock
                            stock.update(branch_id=branchId, company_id=companyId, stock=final_stock,
                                         variant_id=updateStock.variant_id)
                            db.commit()
                            return {"status": 200, "data": {}, "message": "Updated successfully"}

                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.post('/v1.1/{userId}/{companyId}/{branchId}/bookOrder')
def book_order(bookOrder: schemas.BookOrder, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:
                order_items = []
                for items in bookOrder.items_ordered:
                    variant_id = items.get("variant_id")
                    count = items.get("count")

                    variant = db.query(models.Variants).filter(
                        models.Variants.variant_id == variant_id).first()
                    if variant:
                        product = db.query(models.Products).filter(
                            models.Products.product_id == variant.product_id).first()
                        category = db.query(models.Category).filter(
                            models.Category.category_id == product.category_id).first()
                        brand = db.query(models.Brand).filter(
                            models.Brand.brand_id == product.brand_id).first()
                        stock_data = db.query(models.Inventory).filter(
                            models.Inventory.variant_id == variant_id).first()
                        if stock_data.stock == 0:
                            return {"status": 204, "message": f"{product.product_name} is out of stock",
                                    "data": {}}
                        else:
                            if stock_data.stock < count:
                                return {"status": 204,
                                        "message": f"Only {stock_data.stock} available for {product.product_name}.",
                                        "data": {}}
                            else:
                                if brand:
                                    brand_name = brand.brand_name
                                else:
                                    brand_name = None
                                item = {"category_id": category.category_id,
                                        "category_name": category.category_name,
                                        "product_name": product.product_name,
                                        "brand_name": brand_name,
                                        "brand_id": product.brand_id,
                                        "variant_id": variant_id,
                                        "cost": variant.cost,
                                        "quantity": variant.quantity,
                                        "stock": stock_data.stock,
                                        "stock_id": stock_data.stock_id,
                                        "discount_percent": variant.discount_percent,
                                        "product_description": product.product_description,
                                        "images": variant.images,
                                        "unit": variant.unit,
                                        "barcode": variant.barcode,
                                        "draft": variant.draft,
                                        "restock_reminder": variant.restock_reminder,
                                        "SGST": variant.SGST if variant.SGST else 0.0,
                                        "CGST": variant.CGST if variant.CGST else 0.0,
                                        "count": count}
                                order_items.append(item)
                                stock_update_query = db.query(models.Inventory).filter(
                                    models.Inventory.stock_id == variant.stock_id)

                                stock_update_query.update(branch_id=branchId, company_id=companyId,
                                                          stock=stock_data.stock - count,
                                                          variant_id=variant_id)

                                db.commit()

                    else:
                        return {"status": 204, "message": f"Wrong variant id {variant_id}", "data": {}}

                add_order = models.Orders(branch_id=branchId, company_id=companyId, items_ordered=order_items,
                                          customer_contact=bookOrder.customer_contact,
                                          payment_status=bookOrder.payment_status,
                                          payment_type=bookOrder.payment_type,
                                          customer_name=bookOrder.customer_name,
                                          discount_total=bookOrder.discount_total,
                                          total_amount=bookOrder.total_amount,
                                          subtotal=bookOrder.subtotal)
                db.add(add_order)
                db.commit()

                return {"status": 200, "data": {}, "message": "success"}

            else:
                return {"status": 204, "data": {}, "message": "Branch doesnt exist"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.get('/v1.1/{userId}/{companyId}/{branchId}/getAllOrders')
def get_orders(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:

            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:

                orders = db.query(models.Orders).order_by(desc(models.Orders.order_id)).all()
                total_earning = db.query(func.sum(models.Orders.total_amount)).scalar()
                total_order_count = len(orders)
                unpaid_orders = len(db.query(models.Orders).filter(models.Orders.payment_status != 'paid').all())
                payment_method_counts = db.query(models.Orders.payment_type,
                                                 func.count().label('count')).group_by(
                    models.Orders.payment_type).all()

                payment_method_map = {
                    method: {'count': count, 'percent': round(
                        (count / total_order_count) * 100, 1)} for
                    method, count in payment_method_counts}
                get_all_orders = {
                    "total_earning": total_earning if total_earning is not None else 0,
                    "total_orders": total_order_count,
                    "unpaid_order": {"count": unpaid_orders,
                                     "percent": round((
                                                              unpaid_orders / total_order_count) * 100,
                                                      1) if total_order_count != 0 else 0
                                     },
                    "payment_methods": payment_method_map,
                    "orders": []
                }
                for order in orders:
                    get_all_orders["orders"].append({
                        "order_id": order.order_id,
                        "order_number": order.order_no,
                        "order_date": order.order_date,
                        "customer_contact": order.customer_contact,
                        "payment_status": order.payment_status,
                        "payment_type": order.payment_type,
                        "customer_name": order.customer_name,
                        "discount_total": order.discount_total if order.discount_total is not None else 0.0,
                        "total_amount": order.total_amount,
                        "subtotal": order.subtotal,
                        "items_ordered": order.items_ordered,
                        "currency": branch.branch_currency
                    })

                return {"status": 200, "data": get_all_orders, "message": "success"}

            else:
                return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.post('/v1.1/{userId}/{companyId}/{branchId}/addCategory')
def add_category(addCategory: schemas.Categories, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:

            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:

                category_name_exists = db.query(models.Category).filter(
                    models.Category.category_name == addCategory.category_name).first()

                if category_name_exists:
                    return {"status": 204, "data": {},
                            "message": f"Category with {addCategory.category_name} already exists"}

                else:
                    category_added = models.Category(branch_id=branchId, company_id=companyId,
                                                     category_name=addCategory.category_name,
                                                     is_active=addCategory.is_active, modified_by=userId,
                                                     modified_on=datetime.now())
                    db.add(category_added)
                    db.commit()

                    return {"status": 200, "data": {}, "message": "Successfully"}

            else:
                return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.put('/v1.1/{userId}/{companyId}/{branchId}/editCategory')
def edit_category(editCategory: schemas.Categories, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            try:

                branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
                if branch:
                    category_query = db.query(models.Category).filter(
                        models.Category.category_id == editCategory.category_id)
                    category = category_query.first()
                    category_name_exists = db.query(models.Category).filter(
                        models.Category.category_name == editCategory.category_name).filter(
                        models.Category.category_id != editCategory.category_id).first()
                    if category:
                        if category_name_exists:
                            return {"status": 204, "data": {},
                                    "message": f"Category with {editCategory.category_name} already exists"}

                        else:
                            editCategory.modified_by = userId
                            editCategory.modified_on = datetime.now()
                            category_query.update(editCategory.model_dump())
                            db.commit()
                            return {"status": 200, "data": {}, "message": "Successfully"}

                    else:
                        return {"status": 204, "data": {}, "message": "Incorrect category id"}

                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.delete('/v1.1/{userId}/{companyId}/{branchId}/deleteCategory')
def delete_category(deleteCategory: schemas.DeleteCategory, companyId: str, userId: str, branchId: str,
                    db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            try:

                branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
                if branch:
                    category = db.query(models.Category).filter(
                        models.Category.category_id == deleteCategory.category_id).first()
                    if category:
                        if category.category_name == 'uncategorized':
                            return {"status": 204, "data": {}, "message": "Cannot delete this category"}
                        else:
                            products = db.query(models.Products).filter(
                                models.Products.category_id == deleteCategory.category_id).all()
                            resign_category_name = 'uncategorized'
                            resign_category = db.query(models.Category).filter(
                                models.Category.category_name == resign_category_name).first()
                            if resign_category:
                                new_category_id = resign_category.category_id
                            else:
                                category_added = models.Category(branch_id=branchId, company_id=companyId,
                                                                 category_name=resign_category_name)
                                new_category_id = category_added.category_id
                                db.commit()

                            for product in products:
                                product.update(branch_id=branchId, company_id=companyId, category_id=new_category_id,
                                               brand_id=product.brand_id,
                                               product_name=product.product_name,
                                               product_description=product.product_description)
                                db.commit()

                            db.query(models.Category).filter(
                                models.Category.category_id.in_(deleteCategory.category_id)).delete(
                                synchronize_session=False)
                            db.commit()
                            return {"status": 200, "data": {}, "message": "Category deleted successfully"}
                    else:
                        return {"status": 204, "data": {}, "message": "Incorrect category id"}

                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.get('/v1.1/{userId}/{companyId}/{branchId}/getProfile')
def get_profile(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:

            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:
                if company.owner == user.user_id:
                    owner_name = user.user_name
                    owner_contact = user.user_contact
                else:
                    owner = db.query(models.UsersV).filter(models.UsersV.user_id == company.owner).first()
                    owner_name = owner.user_name
                    owner_contact = owner.user_contact

                return {"status": 200, "message": "Success", "data": {
                    "store_logo": company.company_logo if company.company_logo else "",
                    "store_name": company.company_name,
                    "owner_name": owner_name,
                    "owner_contact": owner_contact,
                    "email": "",
                    "address": branch.branch_address
                }}
            else:
                return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.get('/v1.1/{userId}/{companyId}/getAllBranches')
def get_branches(companyId: str, userId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            branches = branch_list(True if company.owner == userId else False, company.company_id, db)
            return {'status': 200, "message": "success", "data": branches}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.put('/v1.1/{userId}/{companyId}/editBranch')
def edit_branch(companyId: str, userId: str, editBranch: schemas.Branch, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            branch_query = db.query(models.Branches).filter(
                models.Branches.branch_id == editBranch.branch_id)
            branch = branch_query.first()
            if branch:
                editBranch.modified_by = userId
                editBranch.modified_on = datetime.now()
                editBranch.company_id = companyId
                branch_query.update(editBranch.model_dump())

                db.commit()
                return {"status": 200, "data": {}, "message": "Successfully"}

            else:
                return {"status": 204, "data": {}, "message": "Incorrect category id"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.post('/v1.1/{userId}/{companyId}/{branchId}/addPaymentMethod')
def add_payment_method(addPaymentType: schemas.Payment, companyId: str, userId: str, branchId: int, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:

            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:
                payment_name_exists = db.query(models.PaymentMethod).filter(
                    models.PaymentMethod.payment_name == addPaymentType.payment_name).first()

                if payment_name_exists:
                    return {"status": 204, "data": {},
                            "message": f"Payment Method with {addPaymentType.category_name} already exists"}

                else:
                    addPaymentType.branch_id = branchId
                    addPaymentType.company_id = companyId
                    addPaymentType.modified_by = userId
                    payment_added = models.PaymentMethod(**addPaymentType.model_dump())
                    db.add(payment_added)
                    db.commit()

                    return {"status": 200, "data": {}, "message": "Successfully"}

            else:
                return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.put('/v1.1/{userId}/{companyId}/{branchId}/editPaymentMethod')
def edit_payment_method(editPayment: schemas.Payment, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:

            branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
            if branch:

                payment_query = db.query(models.PaymentMethod).filter(
                    models.PaymentMethod.payment_id == editPayment.payment_id)
                payment = payment_query.first()
                payment_method_exists = db.query(models.PaymentMethod).filter(
                    models.PaymentMethod.payment_name == editPayment.payment_name).filter(
                    models.PaymentMethod.payment_id != editPayment.payment_id).first()
                if payment:
                    if payment_method_exists:
                        return {"status": 204, "data": {},
                                "message": f"Payment with {editPayment.payment_name} already exists"}

                    else:
                        editPayment.branch_id = branchId
                        editPayment.company_id = companyId
                        editPayment.modified_by = userId
                        editPayment.modified_on = datetime.now()
                        payment_query.update(editPayment.model_dump())

                    db.commit()
                    return {"status": 200, "data": {}, "message": "Successfully"}

                else:
                    return {"status": 204, "data": {}, "message": "Incorrect category id"}

            else:
                return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.delete('/v1.1/{userId}/{companyId}/{branchId}/deletePaymentMethod')
def delete_payment(deletePayment: schemas.DeletePayment, companyId: str, userId: str, branchId: str,
                   db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            try:

                branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
                if branch:
                    payment = db.query(models.PaymentMethod).filter(
                        models.PaymentMethod.payment_id == deletePayment.payment_id).first()
                    if payment:
                        payment.delete(synchronize_session=False)

                        db.commit()
                        return {"status": 200, "data": {}, "message": "Payment Method deleted successfully"}
                    else:
                        return {"status": 204, "data": {}, "message": "Incorrect payment id"}

                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.get('/v1.1/{userId}/{companyId}/{branchId}/getAllPaymentMethods')
def get_all_payment_methods(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.UsersV).get(userId)
    if user:
        company = db.query(models.CompaniesV).get(companyId)
        if company:
            try:

                branch = db.query(models.Branches).filter(models.Branches.branch_id == branchId).first()
                if branch:
                    payments = db.query(models.PaymentMethod).order_by(asc(models.PaymentMethod.payment_id)).all()
                    return schemas.GetAllPaymentMethods(status=200, data=payments, message="Success")

                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@router.post('/v1.1/{user_id}/{company_id}/addCustomer')
def create_customer(user_id: str, company_id: str, customer: UpdateCustomer, db=Depends(get_db)):
    """Adds a new customer"""
    customer_exists = db.query(models.Customer).filter(
        models.Customer.customer_number == customer.customer_number).first()

    if customer_exists:
        return {"message": "Customer with this number already exists"}

    customer.modified_by = user_id
    customer.company_id = company_id
    new_customer = models.Customer(**customer.model_dump())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return {"status": 200, "data": {new_customer}, "message": "Customer created successfully"}


@router.get("/v1.1/{user_id}/getCustomers", response_model=List[AddCustomer])
def get_customers(db=Depends(get_db)):
    """Gets all the customers"""
    customers = db.query(models.Customer).all()

    return customers


@router.get("/v1.1/{user_id}/getCustomer/{customer_number}")
def get_by_number(customer_number: str, db=Depends(get_db)):
    """Gets a customer by number"""
    customer_by_number = db.query(models.Customer).filter(models.Customer.customer_number == customer_number).first()

    if customer_by_number is None:
        return {"status": 204, "data": {}, "message": f"Customer with number {customer_number} doesnt exist"}

    return {"status": 200, "data": {customer_by_number}, "message": f"Customer by number {customer_number}"}


@router.get("/v1.1/{user_id}/{company_id}/getCustomersByCompany", response_model=List[AddCustomer])
def get_customer_by_company(company_id: str, db=Depends(get_db)):
    """Gets all the customers belonging to a particular company"""
    customer_by_company = db.query(models.Customer).filter(models.Customer.company_id == company_id).all()

    return customer_by_company


@router.put("/v1.1/{user_id}/{company_id}/updateCustomer/{customer_number}")
def update_customer(user_id: str, company_id: str, customer_number: str, incoming_customer_data: UpdateCustomer,
                    db=Depends(get_db)):
    """Updates the customer"""
    incoming_customer_data.modified_by = user_id
    incoming_customer_data.modified_on = datetime.now()
    incoming_customer_data.company_id = company_id
    customer_query = db.query(models.Customer).filter(models.Customer.customer_number == customer_number)
    to_be_updated_customer = customer_query.first()

    if to_be_updated_customer is None:
        return {"status": 204, "data": {}, "message": f"Customer with number {customer_number} doesnt exist"}

    updated_customer = customer_query.update(incoming_customer_data.model_dump())
    db.commit()

    return {"status": 200, "message": "Customer updated successfully."}

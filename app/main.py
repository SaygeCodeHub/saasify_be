import logging
import os
import shutil
from typing import List

import firebase_admin
import sqlalchemy
from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, storage
from passlib.context import CryptContext
from sqlalchemy import MetaData, Table, insert, update, delete, desc
from starlette.responses import JSONResponse

from . import models, schemas
from .database import engine, get_db
from .routes import authentication, on_boarding

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
metadata = MetaData()

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

app.include_router(authentication.router)
app.include_router(on_boarding.router)

UPLOAD_DIR = "app/images"
logging.basicConfig(filename='app.log', level=logging.DEBUG)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'saasify-5ddd8.appspot.com',
                                     'databaseURL': 'https://saasify-5ddd8.appspot.com-default-rtdb.firebaseio.com/'})


@app.get('/')
def root():
    return {'message': 'Hello world'}


directory = "app/uploaded_images"
if not os.path.exists(directory):
    os.makedirs(directory)


def save_upload_file(upload_file: UploadFile, destination: str):
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()


@app.post("/v1/uploadImages")
async def upload_images(upload_files: List[UploadFile] = File(...)):
    image_urls = []
    for upload_file in upload_files:
        destination = os.path.join("app", "uploaded_images", upload_file.filename)
        save_upload_file(upload_file, destination)
        bucket = storage.bucket()
        bucket.cors = [
            {
                "origin": ["*"],
                "responseHeader": [
                    "Content-Type",
                    "x-goog-resumable"],
                "method": ['PUT', 'POST', 'GET'],
                "maxAgeSeconds": 3600
            }
        ]
        bucket.patch()
        blob = bucket.blob(f"uploaded_images/{upload_file.filename}")
        blob.upload_from_filename(destination)
        image_url = blob.public_url

        image_urls.append(image_url)
    response_data = {
        "status": 200,
        "message": "Images uploaded successfully.",
        "data": image_urls}
    return JSONResponse(content=response_data)


@app.post('/v1/{userId}/{companyId}/{branchId}/addProduct')
def add_product(createProduct: schemas.AddProducts, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId).first()
                if branch:
                    table_name = f"{companyId}_{branchId}"
                    try:
                        category_table = Table(f"{table_name}_categories", metadata, autoload_with=db.bind)
                        brand_table = Table(table_name + "_brands", metadata, autoload_with=db.bind)
                        products_table = Table(table_name + "_products", metadata, autoload_with=db.bind)
                        variant_table = Table(table_name + "_variants", metadata, autoload_with=db.bind)
                        stock_table = Table(table_name + "_inventory", metadata, autoload_with=db.bind)
                        category = db.query(category_table).filter(
                            category_table.c.category_name == createProduct.category_name).first()
                        if category:
                            category_id = category.category_id
                        else:
                            category_added = insert(category_table).returning(category_table.c.category_id)
                            category_id = db.execute(category_added,
                                                     {"category_name": createProduct.category_name}).fetchone()[0]
                            db.commit()

                        brand_id = None
                        if createProduct.brand_name is not None:

                            brand = db.query(brand_table).filter(
                                brand_table.c.brand_name == createProduct.brand_name).first()
                            if brand:
                                brand_id = brand.brand_id
                            else:
                                brand_added = insert(brand_table).returning(brand_table.c.brand_id)
                                brand_id = db.execute(brand_added,
                                                      {"brand_name": createProduct.brand_name}).fetchone()[0]
                                db.commit()
                        product_id = None
                        if createProduct.product_id:
                            product_check = db.query(products_table).filter(
                                products_table.c.product_id == createProduct.product_id).first()
                            if product_check:
                                product_id = createProduct.product_id
                        else:
                            if brand_id is not None:
                                product = db.query(products_table).filter(
                                    products_table.c.category_id == category_id).filter(
                                    products_table.c.brand_id == brand_id).filter(
                                    products_table.c.product_name == createProduct.product_name).first()
                            else:
                                product = db.query(products_table).filter(
                                    products_table.c.category_id == category_id).filter(
                                    products_table.c.product_name == createProduct.product_name).first()
                            if product:
                                product_id = product.product_id
                            else:
                                product_added = insert(products_table).returning(products_table)
                                products = db.execute(product_added,
                                                      {"category_id": category_id,
                                                       "brand_id": brand_id,
                                                       "product_name": createProduct.product_name,
                                                       "product_description": createProduct.product_description}
                                                      ).fetchone()[0]
                                product_id = products
                                db.commit()
                        if createProduct.barcode:

                            variant = db.query(variant_table).filter(
                                variant_table.c.barcode == createProduct.barcode).first()
                            if variant:
                                return {"status": 204, "data": {}, "message": "variant already exists"}
                            else:
                                if createProduct.stock:
                                    stock_add = insert(stock_table).returning(stock_table)
                                    stock_id = db.execute(stock_add, {"stock": createProduct.stock}).fetchone()[0]
                                    variant_added = insert(variant_table).returning(variant_table)
                                    variant_id = db.execute(variant_added,
                                                            {"product_id": product_id,
                                                             "cost": createProduct.cost,
                                                             "quantity": createProduct.quantity,
                                                             "unit": createProduct.unit,
                                                             "stock_id": stock_id,
                                                             "discount_percent": createProduct.discount_percent,
                                                             "images": createProduct.images,
                                                             "draft": createProduct.draft,
                                                             "barcode": createProduct.barcode,
                                                             "restock_reminder": createProduct.restock_reminder}).fetchone()[
                                        0]
                                    stock_update = update(stock_table).values(stock=createProduct.stock,
                                                                              variant_id=variant_id)
                                    db.execute(stock_update.where(stock_table.c.stock_id == stock_id))
                                    db.commit()

                                    return {"status": 200, "data": {"category_name": createProduct.category_name,
                                                                    "brand_name": createProduct.brand_name,
                                                                    "product_name": createProduct.product_name,
                                                                    "product_id": product_id,
                                                                    "product_description": createProduct.product_description},
                                            "message": "Product Added successfully"}
                                else:
                                    variant_added = insert(variant_table).returning(variant_table)
                                    db.execute(variant_added,
                                               {"product_id": product_id,
                                                "cost": createProduct.cost,
                                                "quantity": createProduct.quantity,
                                                "unit": createProduct.unit,
                                                "stock_id": None,
                                                "discount_percent": createProduct.discount_percent,
                                                "images": createProduct.images,
                                                "draft": createProduct.draft,
                                                "is_active": createProduct.is_active,
                                                "barcode": createProduct.barcode,
                                                "restock_reminder": createProduct.restock_reminder})
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

                    except sqlalchemy.exc.NoSuchTableError:
                        return {"status": 204, "data": {}, "message": "Wrong category table"}
                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except sqlalchemy.exc.NoSuchTableError:
                return {"status": 204, "data": {}, "message": "Wrong branch table"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@app.get('/v1/{userId}/{companyId}/{branchId}/getAllCategories')
def get_add_categories(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId)
                if branch:
                    table_name = companyId + "_" + branchId
                    try:
                        category_table = Table(table_name + "_categories", metadata, autoload_with=db.bind)
                        categories = db.query(category_table).all()
                        return schemas.GetAllCategories(status=200, data=categories, message="get all categories")
                    except sqlalchemy.exc.NoSuchTableError:
                        return schemas.GetAllCategories(status=204, data=[], message="Incorrect company or branch")
                else:
                    return schemas.GetAllCategories(status=204, data=[], message="Branch doesnt exist")

            except sqlalchemy.exc.NoSuchTableError:
                return schemas.GetAllCategories(status=204, data=[], message="Branch doesnt exist")

        else:
            return schemas.GetAllCategories(status=204, data=[], message="Company doesnt exist")

    else:
        return schemas.GetAllCategories(status=204, data=[], message="User doesnt exist")


@app.get('/v1/{userId}/{companyId}/{branchId}/getAllProducts')
def get_add_categories(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId)
                if branch:
                    table_name = companyId + "_" + branchId
                    try:
                        variants_table = Table(table_name + "_variants", metadata, autoload_with=db.bind)
                        category_table = Table(f"{table_name}_categories", metadata, autoload_with=db.bind)
                        product_table = Table(table_name + "_products", metadata, autoload_with=db.bind)
                        brand_table = Table(table_name + "_brands", metadata, autoload_with=db.bind)
                        inventory_table = Table(table_name + "_inventory", metadata, autoload_with=db.bind)

                        products_list = db.query(product_table).all()
                        products_data = []
                        for product in products_list:
                            category = db.query(category_table).filter(
                                category_table.c.category_id == product.category_id).first()
                            brand = db.query(brand_table).filter(brand_table.c.brand_id == product.brand_id).first()
                            variants = db.query(variants_table).filter(
                                variants_table.c.product_id == product.product_id).all()

                            if brand:
                                brand_name = brand.brand_name
                            else:
                                brand_name = None

                            for variant in variants:
                                if variant.stock_id:
                                    stock = db.query(inventory_table).filter(
                                        inventory_table.c.stock_id == variant.stock_id).first()
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
                                    "restock_reminder": variant.restock_reminder
                                })

                        return {"status": 200, "data": products_data, "message": "get all products"}
                    except sqlalchemy.exc.NoSuchTableError:
                        return {"status": 204, "data": [], "message": "incorrect input"}
            except sqlalchemy.exc.NoSuchTableError:
                return {"status": 204, "data": [], "message": "table not exist branch"}
        else:
            return {"status": 204, "data": [], "message": "Company does not exists"}

    else:
        return {"status": 204, "data": [], "message": "User does not exists"}


@app.get('/v1/{userId}/{companyId}/{branchId}/getInventoryProducts')
def get_add_categories(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId)
                if branch:
                    table_name = companyId + "_" + branchId
                    try:
                        variants_table = Table(table_name + "_variants", metadata, autoload_with=db.bind)
                        category_table = Table(f"{table_name}_categories", metadata, autoload_with=db.bind)
                        product_table = Table(table_name + "_products", metadata, autoload_with=db.bind)
                        brand_table = Table(table_name + "_brands", metadata, autoload_with=db.bind)
                        inventory_table = Table(table_name + "_inventory", metadata, autoload_with=db.bind)

                        variants = db.query(variants_table).all()
                        products = []
                        for variant in variants:
                            product = db.query(product_table).filter(
                                product_table.c.product_id == variant.product_id).first()
                            category = db.query(category_table).filter(
                                category_table.c.category_id == product.category_id).first()
                            brand = db.query(brand_table).filter(brand_table.c.brand_id == product.brand_id).first()
                            if brand:
                                brand_name = brand.brand_name
                            else:
                                brand_name = None

                            if variant.stock_id is None:
                                stock_count = 0
                            else:
                                stock = db.query(inventory_table).filter(
                                    inventory_table.c.stock_id == variant.stock_id).first()
                                stock_count = stock.stock
                            if category.is_active:
                                if not variant.draft:
                                    if variant.is_active:
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
                                            "restock_reminder": variant.restock_reminder})

                        return {"status": 200, "data": products, "message": "get all products"}
                    except sqlalchemy.exc.NoSuchTableError:
                        return {"status": 204, "data": [], "message": "incorrect input"}
            except sqlalchemy.exc.NoSuchTableError:
                return {"status": 204, "data": [], "message": "table not exist branch"}
        else:
            return {"status": 204, "data": [], "message": "Company does not exists"}

    else:
        return {"status": 204, "data": [], "message": "User does not exists"}


@app.get('/v1/{userId}/{companyId}/{branchId}/getProductsByCategory')
def get_add_categories(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId)
                if branch:
                    table_name = companyId + "_" + branchId
                    try:
                        variants_table = Table(table_name + "_variants", metadata, autoload_with=db.bind)
                        category_table = Table(f"{table_name}_categories", metadata, autoload_with=db.bind)
                        product_table = Table(table_name + "_products", metadata, autoload_with=db.bind)
                        brand_table = Table(table_name + "_brands", metadata, autoload_with=db.bind)
                        inventory_table = Table(table_name + "_inventory", metadata, autoload_with=db.bind)

                        response_data = []
                        categories = db.query(category_table).filter(category_table.c.is_active == True).all()
                        for category in categories:
                            category_data = {
                                "category_id": category.category_id,
                                "category_name": category.category_name,
                                "products": []
                            }
                            products = db.query(product_table).filter(
                                product_table.c.category_id == category.category_id).all()
                            for product in products:
                                brand = db.query(brand_table).filter(brand_table.c.brand_id == product.brand_id).first()
                                if brand:
                                    brand_name = brand.brand_name
                                else:
                                    brand_name = None

                                variants = db.query(variants_table).filter(
                                    variants_table.c.product_id == product.product_id).filter(
                                    variants_table.c.draft == False).filter(
                                    variants_table.c.is_active == True).all()
                                if variants:
                                    product_data = {
                                        "product_id": product.product_id,
                                        "product_name": product.product_name,
                                        "brand_id": product.brand_id,
                                        "brand_name": brand_name,
                                        "product_description": product.product_description,
                                        "variants": []
                                    }
                                    for variant in variants:
                                        if variant.stock_id is None:
                                            stock_count = 0
                                        else:
                                            stock = db.query(inventory_table).filter(
                                                inventory_table.c.stock_id == variant.stock_id).first()
                                            stock_count = stock.stock

                                        variant_data = {
                                            "variant_id": variant.variant_id,
                                            "cost": variant.cost,
                                            "quantity": variant.quantity,
                                            "discount_percent": variant.discount_percent,
                                            "stock_id": variant.stock_id,
                                            "stock": stock_count,
                                            "images": variant.images,
                                            "unit": variant.unit,
                                            "barcode": variant.barcode,
                                            "restock_reminder": variant.restock_reminder,
                                            "draft": variant.draft}
                                        product_data["variants"].append(variant_data)
                                    category_data["products"].append(product_data)
                            response_data.append(category_data)

                        return {"status": 200, "data": response_data, "message": "get all products"}

                    except sqlalchemy.exc.NoSuchTableError:
                        return {"status": 204, "data": [], "message": "incorrect input"}
                    except Exception as e:
                        return {"status": 204, "data": {}, "message": f"{e}"}

            except sqlalchemy.exc.NoSuchTableError:
                return {"status": 204, "data": [], "message": "table not exist branch"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": [], "message": "Company does not exists"}

    else:
        return {"status": 204, "data": [], "message": "User does not exists"}


@app.put('/v1/{userId}/{companyId}/{branchId}/editProduct')
def edit_product(createProduct: schemas.EditProduct, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId).first()
                if branch:
                    table_name = f"{companyId}_{branchId}"
                    try:
                        category_table = Table(f"{table_name}_categories", metadata, autoload_with=db.bind)
                        brand_table = Table(table_name + "_brands", metadata, autoload_with=db.bind)
                        products_table = Table(table_name + "_products", metadata, autoload_with=db.bind)
                        variant_table = Table(table_name + "_variants", metadata, autoload_with=db.bind)
                        inventory_table = Table(table_name + "_inventory", metadata, autoload_with=db.bind)

                        category = db.query(category_table).filter(
                            category_table.c.category_name == createProduct.category_name).first()
                        if category:
                            category_id = category.category_id
                        else:
                            category_added = insert(category_table).returning(category_table.c.category_id)
                            category_id = db.execute(category_added,
                                                     {"category_name": createProduct.category_name}).fetchone()[0]
                            db.commit()

                        if createProduct.brand_name is not None:
                            brand = db.query(brand_table).filter(
                                brand_table.c.brand_name == createProduct.brand_name).first()
                            if brand:
                                brand_id = brand.brand_id
                            else:
                                brand_added = insert(brand_table).returning(brand_table.c.brand_id)
                                brand_id = db.execute(brand_added,
                                                      {"brand_name": createProduct.brand_name}).fetchone()[0]
                                db.commit()
                        else:
                            brand_id = None

                        if createProduct.product_id:
                            product_check = db.query(products_table).filter(
                                products_table.c.product_id == createProduct.product_id).first()
                            if product_check:
                                product_id = createProduct.product_id
                                update_product = update(products_table).values(category_id=category_id,
                                                                               brand_id=brand_id,
                                                                               product_name=createProduct.product_name,
                                                                               product_description=createProduct.product_description)
                                db.execute(update_product.where(
                                    products_table.c.product_id == product_id))
                                db.commit()

                            else:
                                return {"status": 204, "data": {}, "message": "Invalid product id"}

                            if createProduct.variant_id:
                                variant = db.query(variant_table).filter(
                                    variant_table.c.variant_id == createProduct.variant_id).first()
                                if variant:
                                    stock_update = update(inventory_table).values(stock=createProduct.stock,
                                                                                  variant_id=variant.variant_id)
                                    db.execute(
                                        stock_update.where(inventory_table.c.stock_id == variant.stock_id))
                                    variant_update = update(variant_table).values(product_id=product_id,
                                                                                  cost=createProduct.cost,
                                                                                  stock_id=variant.stock_id,
                                                                                  quantity=createProduct.quantity,
                                                                                  unit=createProduct.unit,
                                                                                  discount_percent=createProduct.discount_percent,
                                                                                  images=createProduct.images,
                                                                                  draft=createProduct.draft,
                                                                                  barcode=createProduct.barcode,
                                                                                  restock_reminder=createProduct.restock_reminder)
                                    db.execute(variant_update.where(
                                        variant_table.c.variant_id == createProduct.variant_id))
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
                                variant = db.query(variant_table).filter(
                                    variant_table.c.barcode == createProduct.barcode).first()
                                if variant:
                                    return {"status": 204, "data": {}, "message": "variant already exists"}
                                else:
                                    stock_add = insert(inventory_table).returning(inventory_table)
                                    stock_id = db.execute(stock_add, {"stock": createProduct.stock}).fetchone()[0]
                                    variant_added = insert(variant_table).returning(variant_table)
                                    variant_id = db.execute(variant_added,
                                                            {"product_id": product_id,
                                                             "cost": createProduct.cost,
                                                             "quantity": createProduct.quantity,
                                                             "unit": createProduct.unit,
                                                             "stock_id": stock_id,
                                                             "discount_percent": createProduct.discount_percent,
                                                             "images": createProduct.images,
                                                             "draft": createProduct.draft,
                                                             "barcode": createProduct.barcode,
                                                             "restock_reminder": createProduct.restock_reminder}).fetchone()[
                                        0]
                                    stock_update = update(inventory_table).values(stock=createProduct.stock,
                                                                                  variant_id=variant_id)
                                    db.execute(
                                        stock_update.where(inventory_table.c.stock_id == stock_id))

                                    db.commit()
                                    return {"status": 200, "data": {"category_name": createProduct.category_name,
                                                                    "brand_name": createProduct.brand_name,
                                                                    "product_name": createProduct.product_name,
                                                                    "product_id": product_id,
                                                                    "product_description": createProduct.product_description},
                                            "message": "Product Edited successfully"}

                    except sqlalchemy.exc.NoSuchTableError:
                        return {"status": 204, "data": {}, "message": "Wrong category tabel"}
                    except Exception as e:
                        return {"status": 204, "data": {}, "message": f"{e}"}
                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except sqlalchemy.exc.NoSuchTableError:
                return {"status": 204, "data": {}, "message": "Wrong branch table"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@app.delete('/v1/{userId}/{companyId}/{branchId}/deleteVariant')
def delete_products(deleteVariants: schemas.DeleteVariants, companyId: str, userId: str, branchId: str,
                    db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId).first()
                if branch:
                    table_name = f"{companyId}_{branchId}"
                    try:
                        variant_table = Table(table_name + "_variants", metadata, autoload_with=db.bind)
                        inventory_table = Table(table_name + "_inventory", metadata, autoload_with=db.bind)
                        for variant in deleteVariants.variant_ids:
                            variant_exists = db.query(variant_table).filter(
                                variant_table.c.variant_id == variant).first()
                            if not variant_exists:
                                return {"status": 204, "data": {}, "message": "Incorrect variant id"}

                        delete_variants = delete(variant_table).where(
                            variant_table.c.variant_id.in_(deleteVariants.variant_ids))
                        delete_stock = delete(inventory_table).where(
                            inventory_table.c.variant_id.in_(deleteVariants.variant_ids))

                        db.execute(delete_variants)
                        db.execute(delete_stock)
                        db.commit()
                        products_table = Table(table_name + "_products", metadata, autoload_with=db.bind)
                        variant_table = Table(table_name + "_variants", metadata, autoload_with=db.bind)

                        products = db.query(products_table).all()
                        for product in products:
                            variants = db.query(variant_table).filter(
                                variant_table.c.product_id == product.product_id).all()
                            if not variants:
                                delete_product = delete(products_table).where(
                                    products_table.c.product_id.in_([product.product_id]))

                                db.execute(delete_product)
                                db.commit()

                        return {"status": 200, "data": {}, "message": "variants deleted successfully"}
                    except sqlalchemy.exc.NoSuchTableError:
                        return {"status": 204, "data": {}, "message": "Wrong variant tabel"}
                    except Exception as e:
                        return {"status": 204, "data": {}, "message": f"{e}"}
                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except sqlalchemy.exc.NoSuchTableError:
                return {"status": 204, "data": {}, "message": "Wrong branch table"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@app.post('/v1/{userId}/{companyId}/{branchId}/updateStock')
def update_stock(updateStock: schemas.UpdateStock, companyId: str, userId: str, branchId: str,
                 db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId).first()
                if branch:
                    table_name = f"{companyId}_{branchId}"
                    try:
                        if not updateStock.stock_id:
                            return {"status": 204, "data": {}, "message": "Invalid stock Id"}
                        else:
                            inventory_table = Table(table_name + "_inventory", metadata, autoload_with=db.bind)
                            stock = db.query(inventory_table).filter(
                                inventory_table.c.stock_id == updateStock.stock_id).first()
                            if not stock:
                                return {"status": 204, "data": {}, "message": "Stock id not found"}
                            else:
                                if updateStock.increment:
                                    final_stock = stock.stock + updateStock.stock
                                else:
                                    final_stock = stock.stock - updateStock.stock
                                stock_update = update(inventory_table).values(stock=final_stock,
                                                                              variant_id=updateStock.variant_id)
                                db.execute(
                                    stock_update.where(inventory_table.c.stock_id == updateStock.stock_id))
                                db.commit()
                                return {"status": 200, "data": {}, "message": "Updated successfully"}

                    except sqlalchemy.exc.NoSuchTableError:
                        return {"status": 204, "data": {}, "message": "Wrong stock tabel"}
                    except Exception as e:
                        return {"status": 204, "data": {}, "message": f"{e}"}
                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except sqlalchemy.exc.NoSuchTableError:
                return {"status": 204, "data": {}, "message": "Wrong branch table"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@app.post('/v1/{userId}/{companyId}/{branchId}/bookOrder')
def book_order(bookOrder: schemas.BookOrder, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId).first()
                if branch:
                    table_name = f"{companyId}_{branchId}"
                    try:
                        orders_table = Table(table_name + "_orders", metadata, autoload_with=db.bind)
                        variants_table = Table(table_name + "_variants", metadata, autoload_with=db.bind)
                        inventory_table = Table(table_name + "_inventory", metadata, autoload_with=db.bind)
                        order_items = []
                        for items in bookOrder.items_ordered:
                            variant_id = items.get("variant_id")
                            count = items.get("count")

                            variant_exists = db.query(variants_table).filter(
                                variants_table.c.variant_id == variant_id).first()
                            if variant_exists:
                                stock_data = db.query(inventory_table).filter(
                                    inventory_table.c.variant_id == variant_id).first()
                                if stock_data.stock == 0:
                                    return {"status": 204, "message": f"{variant_id} is out of stock", "data": {}}
                                else:
                                    if stock_data.stock < count:
                                        return {"status": 204, "message": f"{variant_id} low stock", "data": {}}
                                    else:
                                        item = {"variant_id": variant_id, "count": count}
                                        order_items.append(item)

                                        stock_update = update(inventory_table).values(stock=stock_data.stock - count,
                                                                                      variant_id=variant_id)
                                        db.execute(
                                            stock_update.where(inventory_table.c.stock_id == stock_data.stock_id))
                                        db.commit()

                            else:
                                return {"status": 204, "message": f"Wrong variant id {variant_id}", "data": {}}

                        add_order = insert(orders_table).returning(orders_table)
                        order_id = db.execute(add_order,
                                              {"items_ordered": order_items,
                                               "customer_contact": bookOrder.customer_contact,
                                               "payment_status": bookOrder.payment_status,
                                               "payment_type": bookOrder.payment_type,
                                               "customer_name": bookOrder.customer_name,
                                               "discount_total": bookOrder.discount_total,
                                               "total_amount": bookOrder.total_amount,
                                               "subtotal": bookOrder.subtotal}).fetchone()[0]
                        db.commit()

                        return {"status": 200, "data": {"order_id": order_id}, "message": "success"}

                    except sqlalchemy.exc.NoSuchTableError:
                        return {"status": 204, "data": {}, "message": "Wrong variant tabel"}
                    except Exception as e:
                        return {"status": 204, "data": {}, "message": f"{e}"}

                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except sqlalchemy.exc.NoSuchTableError:
                return {"status": 204, "data": {}, "message": "Wrong branch id"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@app.get('/v1/{userId}/{companyId}/{branchId}/getAllOrders')
def get_orders(companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId).first()
                if branch:
                    table_name = f"{companyId}_{branchId}"
                    try:
                        variants_table = Table(table_name + "_variants", metadata, autoload_with=db.bind)
                        category_table = Table(f"{table_name}_categories", metadata, autoload_with=db.bind)
                        product_table = Table(table_name + "_products", metadata, autoload_with=db.bind)
                        brand_table = Table(table_name + "_brands", metadata, autoload_with=db.bind)
                        inventory_table = Table(table_name + "_inventory", metadata, autoload_with=db.bind)
                        order_table = Table(table_name + "_orders", metadata, autoload_with=db.bind)

                        orders = db.query(order_table).order_by(desc(order_table.c.order_id)).all()
                        orders_list = []
                        for order in orders:
                            items = order.items_ordered
                            ordr_data = {
                                "order_id": order.order_id,
                                "order_number": order.order_no,
                                "order_date": order.order_date,
                                "customer_contact": order.customer_contact,
                                "payment_status": order.payment_status,
                                "payment_type": order.payment_type,
                                "customer_name": order.customer_name,
                                "discount_total": order.discount_total,
                                "total_amount": order.total_amount,
                                "subtotal": order.subtotal,
                                "items_ordered": []
                            }
                            for item in items:
                                variant_id = item.get("variant_id")
                                count = item.get("count")
                                variant = db.query(variants_table).filter(
                                    variants_table.c.variant_id == variant_id).first()
                                if variant:
                                    stock = db.query(inventory_table).filter(
                                        inventory_table.c.stock_id == variant.stock_id).first()
                                    product = db.query(product_table).filter(
                                        product_table.c.product_id == variant.product_id).first()
                                    category = db.query(category_table).filter(
                                        category_table.c.category_id == product.category_id).first()
                                    brand = db.query(brand_table).filter(
                                        brand_table.c.brand_id == product.brand_id).first()
                                    if stock:
                                        stock_count = stock.stock
                                    else:
                                        stock_count = 0

                                    if brand:
                                        brand_name = brand.brand_name
                                    else:
                                        brand_name = None

                                    item_data = {
                                        "category_id": category.category_id,
                                        "category_name": category.category_name,
                                        "product_id": variant.product_id,
                                        "product_name": product.product_name,
                                        "brand_name": brand_name,
                                        "brand_id": product.brand_id,
                                        "variant_id": variant_id,
                                        "cost": variant.cost,
                                        "quantity": variant.quantity,
                                        "discount_percent": variant.discount_percent,
                                        "stock": stock_count,
                                        "stock_id": variant.stock_id,
                                        "product_description": product.product_description,
                                        "images": variant.images,
                                        "unit": variant.unit,
                                        "barcode": variant.barcode,
                                        "draft": variant.draft,
                                        "restock_reminder": variant.restock_reminder,
                                        "count": count}
                                    ordr_data["items_ordered"].append(item_data)
                            orders_list.append(ordr_data)

                        return {"status": 200, "data": orders_list, "message": "success"}

                    except sqlalchemy.exc.NoSuchTableError:
                        return {"status": 204, "data": {}, "message": "Wrong order tabel"}
                    except Exception as e:
                        return {"status": 204, "data": {}, "message": f"{e}"}

                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except sqlalchemy.exc.NoSuchTableError:
                return {"status": 204, "data": {}, "message": "Wrong branch id"}

            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}


@app.put('/v1/{userId}/{companyId}/{branchId}/editCategory')
def edit_category(editCategory: schemas.Categories, companyId: str, userId: str, branchId: str, db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            try:
                branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)

                branch = db.query(branch_table).filter(branch_table.c.branch_id == branchId).first()
                if branch:
                    table_name = f"{companyId}_{branchId}"
                    try:
                        category_table = Table(f"{table_name}_categories", metadata, autoload_with=db.bind)

                        category = db.query(category_table).filter(
                            category_table.c.category_id == editCategory.category_id).first()
                        category_name_exists = db.query(category_table).filter(
                            category_table.c.category_name == editCategory.category_name).filter(
                            category_table.c.category_id != editCategory.category_id).first()
                        if category:
                            if category_name_exists:
                                return {"status": 204, "data": {},
                                        "message": f"Category with {editCategory.category_name} already exists"}

                            else:
                                category_id = editCategory.category_id
                                update_category = update(category_table).values(
                                    category_name=editCategory.category_name,
                                    category_id=category_id,
                                    is_active=editCategory.is_active)
                                db.execute(update_category.where(
                                    category_table.c.category_id == category_id))
                                db.commit()
                                return {"status": 200, "data": {}, "message": "Successfully"}

                        else:
                            return {"status": 204, "data": {}, "message": "Incorrect category id"}

                    except sqlalchemy.exc.NoSuchTableError:
                        return {"status": 204, "data": {}, "message": "Table doesn't exist"}
                else:
                    return {"status": 204, "data": {}, "message": "Branch doesnt exist"}
            except sqlalchemy.exc.NoSuchTableError:
                return {"status": 204, "data": {}, "message": "Wrong branch table"}
            except Exception as e:
                return {"status": 204, "data": {}, "message": f"{e}"}

        else:
            return {"status": 204, "data": {}, "message": "Wrong Company"}

    else:
        return {"status": 204, "data": {}, "message": "un authorized"}

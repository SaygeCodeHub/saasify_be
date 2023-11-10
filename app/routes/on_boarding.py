from fastapi import APIRouter, Depends
from sqlalchemy import MetaData, Table, Column, BIGINT, String, insert, ForeignKey, Double, JSON, Boolean
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db, engine

router = APIRouter()
metadata = MetaData()


@router.post('/v1/{userId}/addCompany')
def add_company(company: schemas.CreateCompany, userId: str, db: Session = Depends(get_db)):
    try:
        user_exists = db.query(models.Users).get(
            userId)
        if user_exists:
            company.owner = userId
            new_company = models.Companies(company_name=company.company_name,
                                           company_domain=company.company_domain, owner=company.owner)
            db.add(new_company)
            db.commit()
            db.refresh(new_company)
            user_company = models.UserCompany(user_id=userId, company_id=new_company.company_id)
            db.add(user_company)
            db.commit()
            company_id = new_company.company_id
            metadata.reflect(bind=db.bind)

            Table(
                company_id + "_branches",
                metadata,
                Column("branch_id", BIGINT, primary_key=True, autoincrement=True),
                Column("branch_name", String, nullable=False),
                Column("branch_address", String, nullable=False),
                Column("branch_contact", BIGINT, nullable=True))
            Table(
                company_id + "_employee",
                metadata,
                Column("employee_id", BIGINT, primary_key=True, autoincrement=True),
                Column("employee_name", String, nullable=True),
                Column("employee_contact", BIGINT, nullable=False),
                Column("employee_password", String, nullable=False),
                Column("employee_gender", String, nullable=True),
                Column("employee_branch_id", BIGINT, nullable=True))
            metadata.create_all(engine)

            branch_table = Table(company_id + "_branches", metadata, autoload_with=db.bind)
            stmt = insert(branch_table).returning(branch_table.c.branch_id)
            inserted_id = db.execute(stmt,
                                     {"branch_name": company.branch_name,
                                      "branch_contact": company.branch_contact,
                                      "branch_address": company.branch_address}).fetchone()[0]
            db.commit()
            if inserted_id:
                metadata.reflect(bind=db.bind)
                table_name = f"{company_id}_{inserted_id}"

                Table(
                    table_name + "_categories",
                    metadata,
                    Column("category_id", BIGINT, primary_key=True, autoincrement=True),
                    Column("category_name", String, nullable=False, unique=True))
                Table(
                    table_name + "_brands",
                    metadata,
                    Column("brand_id", BIGINT, primary_key=True, autoincrement=True),
                    Column("brand_name", String, nullable=False))
                Table(
                    table_name + "_products",
                    metadata,
                    Column("product_id", BIGINT, primary_key=True, autoincrement=True),
                    Column("product_name", String, nullable=False),
                    Column("category_id", BIGINT,
                           ForeignKey(f"{table_name}_categories.category_id", ondelete="CASCADE"), nullable=False),
                    Column("product_description", String, nullable=False),
                    Column("brand_id", BIGINT, ForeignKey(table_name + "_brands.brand_id", ondelete="CASCADE"),
                           nullable=False))
                Table(
                    table_name + "_variants",
                    metadata,
                    Column("variant_id", BIGINT, primary_key=True, autoincrement=True),
                    Column("product_id", BIGINT, ForeignKey(table_name + "_products.product_id", ondelete="CASCADE"),
                           nullable=False),
                    Column("cost", Double, nullable=False),
                    Column("stock", BIGINT, nullable=False),

                    Column("quantity", String, nullable=True),
                    Column("unit", String, nullable=True),
                    Column("discount_cost", Double, nullable=True),
                    Column("discount_percent", Double, nullable=True),
                    Column("images", JSON, nullable=True),
                    Column("draft", Boolean, nullable=True),
                    Column("barcode", BIGINT, nullable=True),
                    Column("restock_reminder", BIGINT, nullable=True))
                Table(
                    table_name + "_inventory",
                    metadata,
                    Column("stock_id", BIGINT, primary_key=True, autoincrement=True),
                    Column("stock", BIGINT, nullable=True),
                    Column("variant_id", BIGINT, ForeignKey(table_name + "_variants.variant_id", ondelete="CASCADE"),
                           nullable=False))

                metadata.create_all(engine)

                return {"status": 200, "message": "branch added successfully", "data": {}}
            else:
                return {"status": 204, "message": "Please enter valid data", "data": {}}

        return {"status": 204, "message": "User doesn't exist", "data": user_exists}

    except Exception as e:
        return {"status": 500, "message": "Something when wrong", "data": {}}

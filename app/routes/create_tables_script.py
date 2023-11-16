from passlib.context import CryptContext
from sqlalchemy import MetaData, Table, Column, BIGINT, String, insert, ForeignKey, Double, JSON, Boolean

from app import models, schemas
from app.database import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
metadata = MetaData()


def create_branch(companyId: str, inserted_id: int, db):
    metadata.reflect(bind=db.bind)
    table_name = f"{companyId}_{inserted_id}"

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
        Column("product_description", String, nullable=True),
        Column("brand_id", BIGINT, ForeignKey(table_name + "_brands.brand_id", ondelete="CASCADE"),
               nullable=True))
    Table(
        table_name + "_variants",
        metadata,
        Column("variant_id", BIGINT, primary_key=True, autoincrement=True),
        Column("product_id", BIGINT, ForeignKey(table_name + "_products.product_id", ondelete="CASCADE"),
               nullable=False),
        Column("cost", Double, nullable=True),
        Column("stock_id", BIGINT, ForeignKey(table_name + "_inventory.stock_id", ondelete="CASCADE"),
               nullable=True),
        Column("quantity", BIGINT, nullable=True),
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
               nullable=True))

    metadata.create_all(engine)


def create_company(companyId: str, company: schemas.CreateCompany, db):
    metadata.reflect(bind=db.bind)

    Table(
        companyId + "_branches",
        metadata,
        Column("branch_id", BIGINT, primary_key=True, autoincrement=True),
        Column("branch_name", String, nullable=False),
        Column("branch_address", String, nullable=False),
        Column("branch_contact", BIGINT, nullable=True))
    Table(
        companyId + "_employee",
        metadata,
        Column("employee_id", BIGINT, primary_key=True, autoincrement=True),
        Column("employee_name", String, nullable=True),
        Column("employee_contact", BIGINT, nullable=False),
        Column("employee_password", String, nullable=False),
        Column("employee_gender", String, nullable=True),
        Column("employee_branch_id", BIGINT, nullable=True))
    metadata.create_all(engine)
    branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)
    stmt = insert(branch_table).returning(branch_table.c.branch_id)
    inserted_id = db.execute(stmt,
                             {"branch_name": company.branch_name,
                              "branch_contact": company.branch_contact,
                              "branch_address": company.branch_address}).fetchone()[0]
    db.commit()
    if inserted_id:
        create_branch(companyId, inserted_id, db)
    else:
        return {"status": 204, "message": "Please enter valid data", "data": {}}

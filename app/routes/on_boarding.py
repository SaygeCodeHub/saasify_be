from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.routes.create_tables_script import create_company, create_branch
from passlib.context import CryptContext
from sqlalchemy import MetaData, Table, insert, Column, BIGINT, String, Boolean

from app import models, schemas
from app.infrastructure.database import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
metadata = MetaData()

router = APIRouter()


@router.post('/v1/{userId}/addCompany')
def add_company(company: schemas.CreateCompany, userId: str, db: Session = Depends(get_db)):
    try:
        user_exists = db.query(models.Users).filter(models.Users.user_id == userId).first()

        if user_exists:
            try:
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
                create_company(company_id, company, db)
                return {"status": 200, "message": "Company added successfully", "data": {}}

            except:
                return {"status": 204, "message": "Something when wrong", "data": {}}

        return {"status": 204, "message": "User doesn't exist", "data": user_exists}

    except Exception as e:
        return {"status": 500, "message": "Something when wrong", "data": {}}


@router.post('/v1/{userId}/{companyId}/addBranch')
def add_branch(createBranch: schemas.Branch, companyId: str, userId: str, db=Depends(get_db)):
    user = db.query(models.Users).get(userId)
    if user:
        company = db.query(models.Companies).get(companyId)
        if company:
            metadata.reflect(bind=db.bind)
            branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)
            stmt = insert(branch_table).returning(branch_table.c.branch_id)
            inserted_id = db.execute(stmt,
                                     {"branch_name": createBranch.branch_name,
                                      "branch_contact": createBranch.branch_contact,
                                      "branch_currency": createBranch.branch_currency,
                                      "branch_active": createBranch.branch_active,
                                      "branch_address": createBranch.branch_address}).fetchone()[0]
            db.commit()
            if inserted_id:
                create_branch(companyId, inserted_id, db)
                return {"status": 200, "message": "branch added successfully", "data": {}}
            else:
                return {"status": 204, "message": "Please enter valid data", "data": {}}
        else:
            return {"status": 204, "message": "Wrong company id", "data": {}}

    else:
        return {"status": 204, "message": "Un Authorized", "data": {}}


@router.post('/v1/createTable')
def add_branch(tableName: str, db=Depends(get_db)):
    meta_data = MetaData()
    meta_data.reflect(bind=db.bind)
    Table(
        tableName + "_payments",
        meta_data,
        Column("payment_id", BIGINT, primary_key=True, autoincrement=True),
        Column("payment_name", String, nullable=False, unique=True),
        Column("is_active", Boolean, nullable=False, server_default='TRUE'))

    meta_data.create_all(engine)


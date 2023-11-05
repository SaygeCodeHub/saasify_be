from fastapi import APIRouter, Depends
from sqlalchemy import MetaData, Table, Column, BIGINT, String, insert
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
        if user_exists is not None:
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
            try:
                branch_table = Table(new_company.company_id + "_branches", metadata, autoload_with=db.bind)

                db.execute(insert(branch_table),
                           {"branch_name": company.branch_name, "branch_contact": company.branch_contact,
                            "branch_address": company.branch_address})

                db.commit()
                return {"status": 200, "message": "Company created successfully",
                        "data": {}}
            except Exception as e:
                db.rollback()
                return {"status": 204, "message": e,
                        "data": {}}

        return {"status": 204, "message": "User doesn't exist", "data": user_exists}

    except Exception as e:
        return {"status": 500, "message": e, "data": {}}

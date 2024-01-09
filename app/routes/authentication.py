from fastapi import APIRouter, Depends
from sqlalchemy import and_, MetaData, Table, asc
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.firebase_scripts import add_firebase_client

router = APIRouter()
metadata = MetaData()


@router.post('/v1/authenticateUser')
def create_user(authentication: schemas.Authentication, db: Session = Depends(get_db)):
    try:
        user_exists = db.query(models.Users).get(
            authentication.user_id)
        companies = []
        if not user_exists:
            try:
                new_user_data = models.Users(
                    **authentication.model_dump())
                db.add(new_user_data)
                db.commit()
                db.refresh(new_user_data)
                add_firebase_client(authentication.user_id)
                return {"status": 200, "message": "User successfully Authenticated",
                        "data": {"user": {"user_name": new_user_data.user_name, "user_id": new_user_data.user_id,
                                          "user_contact": new_user_data.user_contact,
                                          "user_email": new_user_data.user_email}, "companies": []}}
            except Exception:
                return {"status": 204, "message": "User is NOT registered, please sing up",
                        "data": {"user": {}, "companies": []}}

        company_user_data = db.query(models.UserCompany).filter(
            models.UserCompany.user_id == authentication.user_id).all()

        for company in company_user_data:
            company_data = db.query(models.Companies).filter(
                and_(models.Companies.company_id == models.Companies.company_id,
                     models.Companies.company_id == company.company_id)).first()
            owner = True if company_data.owner == authentication.user_id else False

            companies.append({
                "company_id": company_data.company_id,
                "company_domain": company_data.company_domain if company_data.company_domain is not None else "",
                "company_email": company_data.company_email if company_data.company_email is not None else "",
                "company_name": company_data.company_name if company_data.company_name is not None else "",
                "services": company_data.services if company_data.services is not None else "",
                "company_logo": company_data.company_logo if company_data.company_logo is not None else "",
                "onboarding_date": company_data.onboarding_date,
                "is_owner": owner,
                "role": [0] if company_data.owner == authentication.user_id else [1],
                "branches": get_all_branches(owner, company_data.company_id, db)})
        if authentication.user_name == "":
            return {"status": 200, "message": "User successfully Authenticated",
                    "data": {"user": {"user_name": user_exists.user_name, "user_id": user_exists.user_id,
                                      "user_contact": user_exists.user_contact, "user_email": user_exists.user_email},
                             "companies": companies}}

        else:
            update = db.query(models.Users).filter(models.Users.user_id == authentication.user_id).update({
                "user_name": authentication.user_name})
            db.query(update)
            db.commit()

            user_update = db.query(models.Users).get(authentication.user_id)
            return {"status": 200, "message": "User successfully Authenticated",
                    "data": {"user": {"user_name": user_update.user_name, "user_id": user_update.user_id,
                                      "user_contact": user_update.user_contact, "user_email": user_update.user_email},
                             "companies": companies}}
    except Exception as e:
        print(e)
        return {"status": 500, "message": "Database connection failed", "data": {"user": {}, "companies": []}}


def get_all_branches(owner: bool, companyId: str, db=Depends(get_db)):
    metadata.reflect(bind=db.bind)

    branch_table = Table(companyId + "_branches", metadata, autoload_with=db.bind)
    branches = db.query(branch_table).order_by(asc(branch_table.c.branch_id)).all()
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

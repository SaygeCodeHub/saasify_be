from fastapi import APIRouter, Depends, Response
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db

router = APIRouter()


@router.post('/authenticateUser')
def create_user(authentication: schemas.Authentication, response: Response, db: Session = Depends(get_db)):
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

                return {"status": 200, "message": "User successfully Authenticated",
                        "data": {"user_name": new_user_data.user_name, "user_id": new_user_data.user_id,
                                 "user_contact": new_user_data.user_contact, "companies": []}}
            except Exception:
                response.status_code = 200
                return {"status": 204, "message": "User is NOT registered, please sing up", "data": {"companies": []}}

        update = db.query(models.Users).filter(models.Users.user_id == authentication.user_id).update({
            "user_name": authentication.user_name})
        db.query(update)
        db.commit()

        user_update = db.query(models.Users).get(authentication.user_id)
        company_user_data = db.query(models.UserCompany).filter(
            models.UserCompany.user_id == authentication.user_id).all()

        for company in company_user_data:
            company_data = db.query(models.Companies).filter(
                and_(models.Companies.company_id == models.Companies.company_id,
                     models.Companies.company_id == company.company_id)).first()

            companies.append({
                "company_id": company_data.company_id,
                "company_domain": company_data.company_domain if company_data.company_domain is not None else "",
                "company_email": company_data.company_email if company_data.company_email is not None else "",
                "company_name": company_data.company_name if company_data.company_name is not None else "",
                "services": company_data.services if company_data.services is not None else "",
                "company_logo": company_data.company_logo if company_data.company_logo is not None else [],
                "company_contact": company_data.company_contact,
                "company_address": company_data.company_address if company_data.company_address is not None else "",
                "onboarding_date": company_data.onboarding_date
            })

        return {"status": 200, "message": "User successfully Authenticated",
                "data": {"user_name": user_update.user_name, "user_id": user_update.user_id,
                         "user_contact": user_update.user_contact, "companies": companies}}
    except Exception as e:
        response.status_code = 404
        return {"status": 404, "message": e, "data": {"companies": []}}

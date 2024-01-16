"""Service layer for Companies"""
from datetime import datetime

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.domain import models_2
from app.v2_0.domain.schema_2 import AddBranch


def add_branch(branch, user_id, company_id, db):
    """Creates a branch for a company"""
    company_exists = db.query(models_2.Companies).filter(models_2.Companies.company_id == company_id).first()
    if company_exists is None:
        return ResponseDTO("404", "Company not found!", {})

    new_branch = models_2.Branches(branch_name=branch.branch_name, modified_by=user_id, company_id=company_id,
                                   activity_status="ACTIVE",
                                   modified_on=datetime.now(), is_head_quarter=branch.is_head_quarter)
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)

    b = db.query(models_2.UserCompanyBranch).filter(models_2.UserCompanyBranch.user_id == user_id).first()

    if b.branch_id is None:
        db.query(models_2.UserCompanyBranch).filter(models_2.UserCompanyBranch.user_id == user_id).update(
            {"branch_id": new_branch.branch_id})
        db.commit()
    elif b.branch_id != new_branch.branch_id:
        new_rel = models_2.UserCompanyBranch(user_id=user_id, company_id=company_id, branch_id=new_branch.branch_id,
                                             role="OWNER")
        db.add(new_rel)
        db.commit()

    return ResponseDTO("200", "Branch created successfully!", {})


def fetch_branches(company_id, db):
    """Fetches the branches of given company"""
    branches = db.query(models_2.Branches).filter(models_2.Branches.company_id == company_id).all()

    return branches


def modify_branch(branch, user_id, branch_id, company_id, db):
    """Updates a branch"""
    branch_query = db.query(models_2.Branches).filter(models_2.Branches.branch_id == branch_id)
    branch_exists = branch_query.first()

    if branch_exists is None:
        return ResponseDTO("404", "Branch does not exist!", {})

    branch.modified_by = user_id
    branch.company_id = company_id
    branch_query.update(branch.__dict__)
    db.commit()

    return ResponseDTO("200", "Branch data updated!", {})


def add_company(company, user_id, db):
    """Creates a company and adds a branch to it"""
    user_exists = db.query(models_2.Users).filter(models_2.Users.user_id == user_id).first()
    if user_exists is None:
        return ResponseDTO("404", "User does not exist!", {})

    new_company = models_2.Companies(company_name=company.company_name, owner=user_id, modified_by=user_id,
                                     activity_status=company.activity_status)
    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    db.query(models_2.UserCompanyBranch).filter(models_2.UserCompanyBranch.user_id == user_id).update(
        {"company_id": new_company.company_id})
    db.commit()

    db.query(models_2.UserCompanyBranch).filter(models_2.UserCompanyBranch.user_id == user_id).update(
        {"role": "OWNER"})
    db.commit()

    branch = AddBranch
    branch.branch_name = company.branch_name
    branch.is_head_quarter = company.is_head_quarter
    add_branch(branch, user_id, new_company.company_id, db)

    return ResponseDTO("200", "Company created successfully", {})
    # try

    # except Exception as exc:
    #     return ExceptionDTO(exc)


def fetch_company(user_id, db):
    """Fetches all companies owned by a user"""
    existing_company = db.query(models_2.Companies).filter(models_2.Companies.owner == user_id).first()

    return existing_company


def modify_company(company, user_id, db):
    """Updates company data"""
    company_query = db.query(models_2.Companies).filter(models_2.Companies.company_name == company.company_name)
    company_exists = company_query.first()
    if not company_exists:
        return ResponseDTO("404", "Company not found!", {})

    company.modified_on = datetime.now()
    company.modified_by = user_id
    company.owner = user_id
    company.activity_status = company.activity_status
    company_query.update(company.__dict__)
    db.commit()

    return ResponseDTO("200", "Company data updated!", {})


def get_all_user_data(user, ucb, db):
    company = db.query(models_2.Companies).filter(models_2.Companies.company_id == ucb.company_id).first()
    branch = db.query(models_2.Branches).filter(models_2.Branches.branch_id == ucb.branch_id).first()
    role = db.query(models_2.UserCompanyBranch).filter(models_2.UserCompanyBranch.user_id == user.user_id).all()

    role_array = []
    for x in role:
        role_array.append(x.__dict__["role"])

    return {"company_id": company.company_id, "company_name": company.company_name,
            "branches": [
                {"branch_id": branch.branch_id, "branch_name": branch.branch_name, "role": role_array}
            ]
            }

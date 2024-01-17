"""Service layer for Companies"""
from datetime import datetime

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.domain import models
from app.v2_0.domain.schema import AddBranch, CompanySettings


def add_branch_to_ucb(new_branch, user_id, company_id, db):
    """Adds the branch to Users company branch table"""
    b = db.query(models.UserCompanyBranch).filter(models.UserCompanyBranch.user_id == user_id).first()

    if b.branch_id is None:
        db.query(models.UserCompanyBranch).filter(models.UserCompanyBranch.user_id == user_id).update(
            {"branch_id": new_branch.branch_id})
        db.commit()
    elif b.branch_id != new_branch.branch_id:
        new_rel = models.UserCompanyBranch(user_id=user_id, company_id=company_id, branch_id=new_branch.branch_id,
                                           role="OWNER")
        db.add(new_rel)
        db.commit()


def import_hq_settings(branch_id, company_id, user_id, db):
    """It copies the settings of headquarters branch to other branches"""
    hq_settings = db.query(models.CompanySettings).filter(
        models.CompanySettings.company_id == company_id and models.CompanySettings.is_hq_settings == "true").first()
    imported_settings = models.CompanySettings(branch_id=branch_id, modified_by=user_id, company_id=company_id,
                                               modified_on=datetime.now(), is_hq_settings=False,
                                               default_approver=hq_settings.default_approver,
                                               working_days=hq_settings.working_days,
                                               time_in=hq_settings.time_in, time_out=hq_settings.time_out,
                                               timezone=hq_settings.timezone, currency=hq_settings.currency,
                                               overtime_rate=hq_settings.overtime_rate,
                                               overtime_rate_per=hq_settings.overtime_rate_per)
    db.add(imported_settings)
    db.commit()
    db.refresh(imported_settings)

    return ResponseDTO(200, "Settings Imported successfully", {})


def add_branch_settings(company_settings, user_id, db):
    """Adds settings to a branch"""
    get_branch = db.query(models.Branches).filter(models.Branches.branch_id == company_settings.branch_id).first()

    if get_branch.is_head_quarter is True:
        new_settings = models.CompanySettings(branch_id=company_settings.branch_id,
                                              company_id=company_settings.company_id, modified_by=user_id,
                                              modified_on=datetime.now(), is_hq_settings=True,
                                              default_approver=company_settings.default_approver)
        db.add(new_settings)
        db.commit()
        db.refresh(new_settings)
    else:
        import_hq_settings(company_settings.branch_id, company_settings.company_id, user_id, db)

    return ResponseDTO(200, "Settings added!", {})


def modify_branch_settings(settings, user_id, company_id, branch_id, db):
    """Updates the branch settings"""
    existing_settings_query = db.query(models.CompanySettings).filter(models.CompanySettings.branch_id == branch_id)
    existing_settings = existing_settings_query.first()
    settings.modified_on = datetime.now()
    settings.modified_by = user_id
    existing_settings_query.update(settings.__dict__)
    db.commit()

    return ResponseDTO(200, "Settings updated", {})


def fetch_branch_settings(user_id, company_id, branch_id, db):
    user_exists = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if user_exists is None:
        return ResponseDTO(404, "User does not exist!", {})

    company_exists = db.query(models.Companies).filter(models.Companies.company_id == company_id).first()
    if company_exists is None:
        return ResponseDTO(404, "Company does not exist!", {})

    branch_exists = db.query(models.Branches).filter(models.Branches.branch_id == branch_id).first()
    if branch_exists is None:
        return ResponseDTO(404, "Branch does not exist!", {})

    settings = db.query(models.CompanySettings).filter(models.CompanySettings.branch_id == branch_id).first()

    if settings is None:
        return ResponseDTO(404, "Settings do not exist!", {})

    return settings


def add_branch(branch, user_id, company_id, db):
    """Creates a branch for a company"""
    company_exists = db.query(models.Companies).filter(models.Companies.company_id == company_id).first()
    if company_exists is None:
        return ResponseDTO(404, "Company not found!", {})

    new_branch = models.Branches(branch_name=branch.branch_name, modified_by=user_id, company_id=company_id,
                                 activity_status="ACTIVE",
                                 modified_on=datetime.now(), is_head_quarter=branch.is_head_quarter)
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)

    # Adds the branch in Users_Company_Branches table
    add_branch_to_ucb(new_branch, user_id, company_id, db)

    company_settings = CompanySettings
    company_settings.branch_id = new_branch.branch_id
    company_settings.default_approver = user_id
    company_settings.company_id = company_id
    add_branch_settings(company_settings, user_id, db)

    return ResponseDTO(200, "Branch created successfully!", {})


def fetch_branches(user_id, company_id, db):
    """Fetches the branches of given company"""
    user = db.query(models.Users).filter(models.Users.user_id == user_id).first()

    if user is None:
        ResponseDTO(404, "User not found!", {})

    branches = db.query(models.Branches).filter(models.Branches.company_id == company_id).all()
    return branches


def modify_branch(branch, user_id, branch_id, company_id, db):
    """Updates a branch"""
    branch_query = db.query(models.Branches).filter(models.Branches.branch_id == branch_id)
    branch_exists = branch_query.first()

    if branch_exists is None:
        return ResponseDTO(404, "Branch does not exist!", {})

    branch.modified_by = user_id
    branch.company_id = company_id
    branch_query.update(branch.__dict__)
    db.commit()

    return ResponseDTO(200, "Branch data updated!", {})


def add_company(company, user_id, db):
    """Creates a company and adds a branch to it"""
    user_exists = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if user_exists is None:
        return ResponseDTO(404, "User does not exist!", {})

    new_company = models.Companies(company_name=company.company_name, owner=user_id, modified_by=user_id,
                                   activity_status=company.activity_status)
    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    db.query(models.UserCompanyBranch).filter(models.UserCompanyBranch.user_id == user_id).update(
        {"company_id": new_company.company_id})
    db.commit()

    db.query(models.UserCompanyBranch).filter(models.UserCompanyBranch.user_id == user_id).update(
        {"role": "OWNER"})
    db.commit()

    branch = AddBranch
    branch.branch_name = company.branch_name
    branch.is_head_quarter = company.is_head_quarter
    add_branch(branch, user_id, new_company.company_id, db)

    return ResponseDTO(200, "Company created successfully", {})
    # try

    # except Exception as exc:
    #     return ExceptionDTO(exc)


def fetch_company(user_id, db):
    """Fetches all companies owned by a user"""
    existing_company = db.query(models.Companies).filter(models.Companies.owner == user_id).first()

    return existing_company


def modify_company(company, user_id,company_id, db):
    """Updates company data"""
    company_query = db.query(models.Companies).filter(models.Companies.company_id == company_id)
    company_exists = company_query.first()
    if not company_exists:
        return ResponseDTO(404, "Company not found!", {})

    company.modified_on = datetime.now()
    company.modified_by = user_id
    company.owner = user_id
    company.activity_status = company.activity_status
    company_query.update(company.__dict__)
    db.commit()

    return ResponseDTO(200, "Company data updated!", {})


def get_all_user_data(user, ucb, db):
    company = db.query(models.Companies).filter(models.Companies.company_id == ucb.company_id).first()
    branch = db.query(models.Branches).filter(models.Branches.branch_id == ucb.branch_id).first()
    role = db.query(models.UserCompanyBranch).filter(models.UserCompanyBranch.user_id == user.user_id).all()

    role_array = []
    for x in role:
        role_array.append(x.__dict__["role"])

    return {"company_id": company.company_id, "company_name": company.company_name,
            "branches": [
                {"branch_id": branch.branch_id, "branch_name": branch.branch_name, "role": role_array}
            ]
            }

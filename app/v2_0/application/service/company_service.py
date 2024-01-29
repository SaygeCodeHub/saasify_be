"""Service layer for Companies"""
from datetime import datetime

from sqlalchemy import select

from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.domain.models.branch_settings import BranchSettings
from app.v2_0.domain.models.branches import Branches
from app.v2_0.domain.models.companies import Companies
from app.v2_0.domain.models.user_auth import UsersAuth
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.models.user_details import UserDetails
from app.v2_0.domain.schemas.branch_schemas import AddBranch
from app.v2_0.domain.schemas.branch_settings_schemas import GetBranchSettings, BranchSettingsSchema
from app.v2_0.domain.schemas.company_schemas import GetCompany
from app.v2_0.domain.schemas.utility_schemas import UserDataResponse


def set_employee_leaves(settings, company_id, db):
    users = db.query(UserCompanyBranch).filter(UserCompanyBranch.company_id == company_id).all()
    user_id_array = []
    for user in users:
        user_id_array.append(user.user_id)
    for ID in user_id_array:
        query = db.query(UserDetails).filter(UserDetails.user_id == ID)
        u = query.first()
        if u.medical_leaves is None and u.casual_leaves is None:
            query.update(
                {"medical_leaves": settings.total_medical_leaves, "casual_leaves": settings.total_casual_leaves})
            db.commit()


def modify_branch_settings(settings, user_id, company_id, branch_id, db):
    """Updates the branch settings"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            existing_settings_query = db.query(BranchSettings).filter(
                BranchSettings.branch_id == branch_id)
            settings.modified_on = datetime.now()
            settings.modified_by = user_id
            existing_settings_query.update(settings.__dict__)
            db.commit()
            set_employee_leaves(settings, company_id, db)

            return ResponseDTO(200, "Settings updated", {})
        else:
            return check

    except Exception as exc:
        return ExceptionDTO("modify_branch_settings", exc)


def fetch_branch_settings(user_id, company_id, branch_id, db):
    """Fetches the branch settings"""
    try:

        user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user_exists is None:
            return ResponseDTO(404, "User does not exist!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            settings = db.query(BranchSettings).filter(BranchSettings.branch_id == branch_id).first()

            if settings is None:
                return ResponseDTO(404, "Settings do not exist!", {})

            result = GetBranchSettings(**settings.__dict__)

            return ResponseDTO(200, "Settings fetched!", result)
        else:
            return check

    except Exception as exc:
        return ExceptionDTO("fetch_branch_settings", exc)


def import_hq_settings(branch_id, company_id, user_id, db):
    """It copies the settings of headquarters branch to other branches"""
    try:
        hq_settings = db.query(BranchSettings).filter(
            BranchSettings.company_id == company_id).filter(
            BranchSettings.is_hq_settings == "true").first()
        imported_settings = BranchSettings(branch_id=branch_id, modified_by=user_id, company_id=company_id,
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
    except Exception as exc:
        return ExceptionDTO("import_hq_settings", exc)


def add_branch_settings(company_settings, user_id, db):
    """Adds settings to a branch"""
    try:
        get_branch = db.query(Branches).filter(Branches.branch_id == company_settings.branch_id).first()

        if get_branch.is_head_quarter is True:
            new_settings = BranchSettings(branch_id=company_settings.branch_id,
                                          company_id=company_settings.company_id, modified_by=user_id,
                                          modified_on=datetime.now(), is_hq_settings=True,
                                          default_approver=company_settings.default_approver)
            db.add(new_settings)
            db.commit()
            db.refresh(new_settings)
        else:
            import_hq_settings(company_settings.branch_id, company_settings.company_id, user_id, db)

        return ResponseDTO(200, "Settings added!", {})
    except Exception as exc:
        return ExceptionDTO("add_branch_settings", exc)


def set_branch_settings(new_branch, user_id, company_id, db):
    """Sets the branch settings"""
    company_settings = BranchSettingsSchema
    company_settings.branch_id = new_branch.branch_id
    company_settings.default_approver = user_id
    company_settings.company_id = company_id
    add_branch_settings(company_settings, user_id, db)


def add_branch_to_ucb(new_branch, user_id, company_id, db):
    """Adds the branch to Users company branch table"""
    try:
        b = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()

        if b.branch_id is None:
            db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).update(
                {"branch_id": new_branch.branch_id})
            db.commit()
        elif b.branch_id != new_branch.branch_id:
            user = db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).first()
            approvers_list = user.approvers
            new_branch_in_ucb = UserCompanyBranch(user_id=user_id, company_id=company_id,
                                                  branch_id=new_branch.branch_id,
                                                  roles=["OWNER"], approvers=approvers_list)
            db.add(new_branch_in_ucb)
            db.commit()
    except Exception as exc:
        return ExceptionDTO("add_branch_to_ucb", exc)


def add_branch(branch, user_id, company_id, db, is_init: bool):
    """Creates a branch for a company"""
    try:
        company_exists = db.query(Companies).filter(Companies.company_id == company_id).first()
        if company_exists is None:
            return ResponseDTO(404, "Company not found!", {})

        new_branch = Branches(branch_name=branch.branch_name, modified_by=user_id, company_id=company_id,
                              activity_status="ACTIVE",
                              modified_on=datetime.now(), is_head_quarter=branch.is_head_quarter)
        db.add(new_branch)
        db.commit()
        db.refresh(new_branch)

        # Adds the branch in Users_Company_Branches table
        add_branch_to_ucb(new_branch, user_id, company_id, db)
        set_branch_settings(new_branch, user_id, company_id, db)
        if is_init:
            return {"branch_name": new_branch.branch_name, "branch_id": new_branch.branch_id}
        else:
            return ResponseDTO(200, "Branch created successfully!",
                               {"branch_name": new_branch.branch_name, "branch_id": new_branch.branch_id})
    except Exception as exc:
        return ExceptionDTO("Add branch", exc)


def fetch_branches(user_id, company_id, branch_id, db):
    """Fetches the branches of given company"""
    try:
        user = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user is None:
            ResponseDTO(404, "User not found!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            branches = db.query(Branches).filter(Branches.company_id == company_id).all()
            return ResponseDTO(200, "Branches fetched!", branches)
        else:
            return check

    except Exception as exc:
        return ExceptionDTO("fetch_branches", exc)


def modify_branch(branch, user_id, company_id, branch_id, bran_id, db):
    """Updates a branch"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            branch_query = db.query(Branches).filter(Branches.branch_id == bran_id)

            if branch_query.first() is None:
                return ResponseDTO(404, "Branch to be updated does not exist!", {})

            branch.modified_by = user_id
            branch.modified_on = datetime.now()
            branch.company_id = company_id
            branch_query.update(branch.__dict__)
            db.commit()

            return ResponseDTO(200, "Branch data updated!", {})
        else:
            return check

    except Exception as exc:
        return ExceptionDTO("modify_branch", exc)


def add_company_to_ucb(new_company, user_id, db):
    """Adds the company to ucb table"""
    try:
        db.query(UserCompanyBranch).filter(UserCompanyBranch.user_id == user_id).update(
            {"company_id": new_company.company_id, "roles": ["OWNER"]})
        db.commit()
    except Exception as exc:
        return ExceptionDTO("add_company_to_ucb", exc)


def add_company(company, user_id, db):
    """Creates a company and adds a branch to it"""
    try:
        user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user_exists is None:
            return ResponseDTO(404, "User does not exist!", {})

        new_company = Companies(company_name=company.company_name, owner=user_id, modified_by=user_id,
                                activity_status=company.activity_status)
        db.add(new_company)
        db.commit()
        db.refresh(new_company)

        add_company_to_ucb(new_company, user_id, db)

        branch = AddBranch
        branch.branch_name = company.branch_name
        branch.is_head_quarter = company.is_head_quarter
        init_branch = add_branch(branch, user_id, new_company.company_id, db, True)

        return ResponseDTO(200, "Company created successfully",
                           {"company_id": new_company.company_id, "company_name": new_company.company_name,
                            "branch": init_branch})
    except Exception as exc:
        return ExceptionDTO("add_company", exc)


def fetch_company(user_id, company_id, branch_id, db):
    """Fetches all companies owned by a user"""
    try:
        user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user_exists is None:
            return ResponseDTO(404, "User does not exist!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            existing_companies_query = db.query(Companies).filter(
                Companies.owner == user_id).all()

            existing_companies = [
                GetCompany(
                    company_id=company.company_id,
                    company_name=company.company_name,
                    owner=company.owner,
                    activity_status=company.activity_status
                )
                for company in existing_companies_query
            ]
            return ResponseDTO(200, "Companies fetched!", {"user_id": user_id, "companies": existing_companies})
        else:
            return check

    except Exception as exc:
        return ExceptionDTO("fetch_company", exc)


def modify_company(company, user_id, company_id, branch_id, comp_id, db):
    """Updates company data"""
    try:
        user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user_exists is None:
            return ResponseDTO(404, "User does not exist!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            company_query = db.query(Companies).filter(Companies.company_id == comp_id)
            if company_query.first() is None:
                return ResponseDTO(404, "The company to be updated does not exist!", {})

            company.modified_on = datetime.now()
            company.modified_by = user_id
            company.owner = user_id
            company.activity_status = company.activity_status
            company_query.update(company.__dict__)
            db.commit()

            return ResponseDTO(200, "Company data updated!", {})
        else:
            return check

    except Exception as exc:
        return ExceptionDTO("modify_company", exc)


def get_all_user_data(ucb, db):
    try:
        company = db.query(Companies).filter(Companies.company_id == ucb.company_id).first()

        stmt = select(UserCompanyBranch.branch_id, UserCompanyBranch.roles,
                      Branches.branch_name).select_from(UserCompanyBranch).join(
            Branches, UserCompanyBranch.branch_id == Branches.branch_id).filter(
            UserCompanyBranch.user_id == ucb.user_id)

        branches = db.execute(stmt)
        result = [
            UserDataResponse(
                branch_id=branch.branch_id,
                branch_name=branch.branch_name,
                roles=branch.roles
            )
            for branch in branches
        ]

        return {"company_id": company.company_id, "company_name": company.company_name,
                "branches": result
                }
    except Exception as exc:
        return ExceptionDTO("get_all_user_data", exc)

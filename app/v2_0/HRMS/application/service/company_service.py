"""Service layer for Companies"""
from datetime import datetime, time

from dateutil.relativedelta import relativedelta
from sqlalchemy import select

from app.v2_0.dto.dto_classes import ResponseDTO
from app.v2_0.HRMS.application.service.ucb_service import add_init_branch_to_ucb, add_company_to_ucb, \
    add_new_branch_to_ucb
from app.v2_0.HRMS.application.service.ucb_service import add_init_branch_to_ucb, add_company_to_ucb, \
    add_new_branch_to_ucb
from app.v2_0.HRMS.application.utility.app_utility import check_if_company_and_branch_exist
from app.v2_0.HRMS.domain.models.branch_settings import BranchSettings
from app.v2_0.HRMS.domain.models.branches import Branches
from app.v2_0.HRMS.domain.models.companies import Companies
from app.v2_0.HRMS.domain.models.module_subscriptions import ModuleSubscriptions
from app.v2_0.HRMS.domain.models.user_auth import UsersAuth
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.HRMS.domain.models.user_details import UserDetails
from app.v2_0.HRMS.domain.schemas.branch_schemas import AddBranch, CreateBranchResponse, UpdateBranch
from app.v2_0.HRMS.domain.schemas.branch_settings_schemas import BranchSettingsSchema, \
    UpdateBranchSettings, GetBranchSettings
from app.v2_0.HRMS.domain.schemas.company_schemas import GetCompany, AddCompanyResponse
from app.v2_0.HRMS.domain.schemas.leaves_schemas import ApproverData
from app.v2_0.HRMS.domain.schemas.utility_schemas import UserDataResponse, GetUserDataResponse
from app.v2_0.dto.dto_classes import ResponseDTO
from app.v2_0.enums import ActivityStatus, Modules


def set_employee_leaves(settings, company_id, db):
    users = db.query(UserCompanyBranch).filter(UserCompanyBranch.company_id == company_id).all()
    user_id_array = []
    for user in users:
        user_id_array.append(user.user_id)
    for ID in user_id_array:
        query = db.query(UserDetails).filter(UserDetails.user_id == ID)
        u = query.first()
        if u is None:
            return ResponseDTO(404, "User not found!", {})
        if u.medical_leaves is None and u.casual_leaves is None:
            query.update(
                {"medical_leaves": settings.total_medical_leaves, "casual_leaves": settings.total_casual_leaves})
            db.flush()


def modify_branch_settings(settings: UpdateBranchSettings, user_id, company_id, branch_id, db):
    """Updates the branch settings"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            existing_settings_query = db.query(BranchSettings).filter(
                BranchSettings.branch_id == branch_id)
            settings.modified_on = datetime.now()
            settings.modified_by = user_id
            company = db.query(Companies).filter(
                Companies.company_id == existing_settings_query.first().company_id).first()

            if settings.default_approver != company.owner:
                return ResponseDTO(400, "Default approver should be the company owner!", {})

            existing_settings_query.update(
                {"working_days": settings.working_days, "time_in": settings.time_in, "time_out": settings.time_out,
                 "timezone": settings.timezone, "currency": settings.currency, "overtime_rate": settings.overtime_rate,
                 "overtime_rate_per": settings.overtime_rate_per, "default_approver": settings.default_approver})
            set_employee_leaves(settings, company_id, db)

            branch = db.query(Branches).filter(Branches.branch_id == branch_id)
            branch.update({"branch_address": settings.branch_address, "pincode": settings.pincode,
                           "longitude": settings.longitude, "latitude": settings.longitude})

            db.commit()

            return ResponseDTO(200, "Settings updated", {})
        else:
            return check
    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def get_approver_data(approver_id, db):
    approver = db.query(UserDetails).filter(UserDetails.user_id == approver_id).first()
    return ApproverData(id=approver_id, approver_name=approver.first_name + " " + approver.last_name)


def fetch_branch_settings(user_id, company_id, branch_id, db):
    """Fetches the branch settings"""
    try:

        user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user_exists is None:
            return ResponseDTO(404, "User does not exist!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            settings = db.query(BranchSettings).filter(BranchSettings.branch_id == branch_id).first()
            if settings is None:
                return ResponseDTO(404, "Settings do not exist!", {})

            settings.default_approver = get_approver_data(settings.default_approver, db)
            branch_data = db.query(Branches).filter(Branches.branch_id == branch_id).first()
            setting_data = settings.__dict__
            setting_data.update(branch_data.__dict__)
            result = GetBranchSettings(**setting_data)

            return ResponseDTO(200, "Settings fetched!", result)
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def import_hq_settings(branch_id, company_id, user_id, db):
    """It copies the settings of headquarters branch to other branches"""
    try:
        hq_settings = db.query(BranchSettings).filter(
            BranchSettings.company_id == company_id).filter(
            BranchSettings.is_hq_settings == "true").first()

        imported_settings = BranchSettings(branch_id=branch_id, company_id=company_id,
                                           is_hq_settings=False,
                                           default_approver=hq_settings.default_approver,
                                           working_days=hq_settings.working_days, total_casual_leaves=3,
                                           total_medical_leaves=12,
                                           time_in=hq_settings.time_in, time_out=hq_settings.time_out,
                                           timezone=hq_settings.timezone, currency=hq_settings.currency,
                                           overtime_rate=hq_settings.overtime_rate,
                                           overtime_rate_per=hq_settings.overtime_rate_per)
        db.add(imported_settings)

        return ResponseDTO(200, "Settings Imported successfully", {})
    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def add_branch_settings(company_settings, user_id, db):
    """Adds settings to a branch"""
    try:
        get_branch = db.query(Branches).filter(Branches.branch_id == company_settings.branch_id).first()

        if get_branch.is_head_quarter is True:
            new_settings = BranchSettings(branch_id=company_settings.branch_id,
                                          time_in=datetime.combine(datetime.now().date(), time(9, 30)),
                                          time_out=datetime.combine(datetime.now().date(), time(18, 30)),
                                          company_id=company_settings.company_id,
                                          is_hq_settings=True, total_casual_leaves=3,
                                          total_medical_leaves=12, overtime_rate_per="HOUR",
                                          default_approver=company_settings.default_approver)
            db.add(new_settings)

        else:
            import_hq_settings(company_settings.branch_id, company_settings.company_id, user_id, db)

        return ResponseDTO(200, "Settings added!", {})
    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def set_branch_settings(new_branch, user_id, company_id, db):
    """Sets the branch settings"""
    company_settings = BranchSettingsSchema
    company_settings.branch_id = new_branch.branch_id
    company_settings.default_approver = user_id
    company_settings.company_id = company_id

    add_branch_settings(company_settings, user_id, db)


def add_new_branch(branch, user_id, branch_id, company_id, db):
    try:
        company_exists = db.query(Companies).filter(Companies.company_id == company_id).first()
        if company_exists is None:
            return ResponseDTO(404, "Company not found!", {})

        new_branch = Branches(branch_name=branch.branch_name, company_id=company_id,
                              activity_status=ActivityStatus.ACTIVE,
                              is_head_quarter=branch.is_head_quarter)
        db.add(new_branch)
        db.flush()
        add_new_branch_to_ucb(new_branch, user_id, company_id, db)
        set_branch_settings(new_branch, user_id, company_id, db)

        module_start_date = datetime.now().date()
        module_end_date = module_start_date + relativedelta(months=6)
        new_module_subscription = ModuleSubscriptions(branch_id=new_branch.branch_id,
                                                      company_id=company_id,
                                                      module_name=[Modules.HR],
                                                      start_date=module_start_date,
                                                      end_date=module_end_date)
        db.add(new_module_subscription)

        db.commit()

        return ResponseDTO(200, "Branch created successfully!",
                           CreateBranchResponse(branch_name=new_branch.branch_name, branch_id=new_branch.branch_id))
    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def get_accessible_modules(new_branch, db):
    # Fetches the ucb entry of newly stored branch
    branch_in_ucb = db.query(UserCompanyBranch).filter(UserCompanyBranch.branch_id == new_branch.branch_id).first()
    return branch_in_ucb.accessible_modules


def add_init_branch(branch, user_id, company_id, db):
    """Creates a branch for a company"""

    company_exists = db.query(Companies).filter(Companies.company_id == company_id).first()
    if company_exists is None:
        return ResponseDTO(404, "Company not found!", {})

    new_branch = Branches(branch_name=branch.branch_name, company_id=company_id,
                          activity_status=ActivityStatus.ACTIVE,
                          is_head_quarter=branch.is_head_quarter)
    db.add(new_branch)
    db.flush()

    # Adds the branch in Users_Company_Branches table
    add_init_branch_to_ucb(new_branch, user_id, company_id, db)

    set_branch_settings(new_branch, user_id, company_id, db)

    # Adds HR module by default to the branch
    # module = ModuleSchema
    # module.modules = [Modules.HR]
    # add_module(module, user_id, new_branch.branch_id, company_id, db)
    return CreateBranchResponse(branch_name=new_branch.branch_name, branch_id=new_branch.branch_id)


def fetch_branches(user_id, company_id, branch_id, db):
    """Fetches the branches of given company"""
    try:
        user = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user is None:
            ResponseDTO(404, "User not found!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

        if check is None:
            branches = db.query(Branches).filter(Branches.company_id == company_id).all()
            return ResponseDTO(200, "Branches fetched!", branches)
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def modify_branch(branch: UpdateBranch, user_id, company_id, branch_id, bran_id, db):
    """Updates a branch"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

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
        return ResponseDTO(204, str(exc), {})


def add_company(company, user_id, db):
    """Creates a company and adds a branch to it"""
    # try:
    user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
    if user_exists is None:
        return ResponseDTO(404, "User does not exist!", {})

    if company.company_name is None:
        return ResponseDTO(204, "Please enter company name!", {})

    new_company = Companies(company_name=company.company_name, owner=user_id, modified_by=user_id,
                            activity_status=company.activity_status)
    db.add(new_company)
    db.flush()

    add_company_to_ucb(new_company, user_id, db)

    branch = AddBranch
    branch.branch_name = company.branch_name
    branch.is_head_quarter = company.is_head_quarter
    init_branch = add_init_branch(branch, user_id, new_company.company_id, db)

    module_start_date = datetime.now().date()
    module_end_date = module_start_date + relativedelta(months=6)
    new_module_subscription = ModuleSubscriptions(branch_id=init_branch.branch_id,
                                                  company_id=new_company.company_id,
                                                  module_name=[Modules.HR],
                                                  start_date=module_start_date,
                                                  end_date=module_end_date)
    db.add(new_module_subscription)

    db.commit()

    return ResponseDTO(200, "Company created successfully",
                       AddCompanyResponse(company_name=new_company.company_name, company_id=new_company.company_id,
                                          branch=init_branch))


# except Exception as exc:
#     return ResponseDTO(204, str(exc), {})


def fetch_company(user_id, company_id, branch_id, db):
    """Fetches all companies owned by a user"""
    try:
        user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user_exists is None:
            return ResponseDTO(404, "User does not exist!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

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
        return ResponseDTO(204, str(exc), {})


def modify_company(company, user_id, company_id, branch_id, comp_id, db):
    """Updates company data"""
    try:
        user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user_exists is None:
            return ResponseDTO(404, "User does not exist!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, user_id, db)

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
        return ResponseDTO(204, str(exc), {})


def get_designation_names(designations):
    designation_names = []
    for designation in designations:
        designation_names.append(designation.name)
    return designation_names


def get_all_user_data(ucb, db):
    company = db.query(Companies).filter(Companies.company_id == ucb.company_id).first()

    stmt = select(UserCompanyBranch.branch_id, UserCompanyBranch.designations,
                  UserCompanyBranch.accessible_features,
                  UserCompanyBranch.accessible_modules,
                  Branches.branch_name).select_from(UserCompanyBranch).join(
        Branches, UserCompanyBranch.branch_id == Branches.branch_id).filter(
        UserCompanyBranch.user_id == ucb.user_id)

    branches = db.execute(stmt)
    result = [
        UserDataResponse(
            branch_id=branch.branch_id,
            branch_name=branch.branch_name,
            designations=get_designation_names(branch.designations),
            accessible_modules=branch.accessible_modules,
            accessible_features=branch.accessible_features
        )
        for branch in branches
    ]

    return GetUserDataResponse(company_id=company.company_id, company_name=company.company_name, branches=result)

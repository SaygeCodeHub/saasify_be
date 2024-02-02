"""Service layer for Modules"""
from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist, add_module_to_ucb
from app.v2_0.domain.models.enums import Modules
from app.v2_0.domain.models.module_subscriptions import ModuleSubscriptions
from app.v2_0.domain.models.user_auth import UsersAuth
from app.v2_0.domain.schemas.module_schemas import GetSubscribedModules, ModuleInfoResponse


def modify_company_modules():
    pass


def add_module(module, user_id, branch_id, company_id, db):
    """Adds modules to a company"""
    try:
        user = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()

        if user is None:
            return ResponseDTO(404, f"User with user id: {user_id} not found", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            for m in module.modules:
                new_module = ModuleSubscriptions(company_id=company_id, branch_id=branch_id, module_name=m)
                db.add(new_module)
                db.commit()

            add_module_to_ucb(branch_id, user_id, module.modules, db)

            return ResponseDTO(200, "Module(s) added successfully", {})
        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def fetch_subscribed_modules(user_id, company_id, branch_id, db):
    try:
        user = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()

        if user is None:
            return ResponseDTO(404, f"User with user id: {user_id} not found", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            modules = db.query(ModuleSubscriptions).filter(ModuleSubscriptions.branch_id == branch_id).all()

            if len(modules) == 0:
                return ResponseDTO(200, "No modules to fetch!", {})

            result = [GetSubscribedModules(module_name=module.module_name.name, is_subscribed=module.is_subscribed,
                                           start_date=module.start_date, end_date=module.end_date)
                      for module in modules
                      ]

            return ResponseDTO(200, "Modules fetched!", result)

        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def fetch_all_modules(user_id, company_id, branch_id, db):
    try:
        user = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()

        if user is None:
            return ResponseDTO(404, f"User with user id: {user_id} not found", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:

            all_modules = list(Modules.__members__)

            result = [
                ModuleInfoResponse(module_name=module)
                for module in all_modules
            ]

            return ResponseDTO(200, "Modules fetched!", result)

        else:
            return check
    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
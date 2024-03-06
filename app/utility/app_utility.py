"""Contains the code that acts as a utility to various files"""
from typing import Optional, List

from app.dto.dto_classes import ResponseDTO
from app.enums.features_enum import Features
from app.v2_0.HRMS.domain.models.branches import Branches
from app.v2_0.HRMS.domain.models.companies import Companies
from app.v2_0.HRMS.domain.models.user_company_branch import UserCompanyBranch
from app.enums.form_type_enum import FormTypeEnum


def check_if_company_and_branch_exist(company_id, branch_id, user_id, db):
    company = db.query(Companies).filter(Companies.company_id == company_id).first()
    if company is None:
        return ResponseDTO(404, "Company not found!", {})

    branch = db.query(Branches).filter(Branches.branch_id == branch_id).first()
    if branch is None:
        return ResponseDTO(404, "Branch not found!", {})

    if user_id:
        ucb = db.query(UserCompanyBranch).filter(UserCompanyBranch.company_id == company_id).filter(
            UserCompanyBranch.branch_id == branch_id).filter(UserCompanyBranch.user_id == user_id).first()
        if ucb is None:
            return ResponseDTO(409, "Unauthorized user!", {})

    return None


def get_all_features(module_array):
    features = []
    for module in module_array:
        for feature in list(Features.__members__):
            if feature.startswith(module.name):
                features.append(feature)
    return features


def ensure_optional_fields(self):
    for field in self.__annotations__:
        if field in self.__dict__ and self.__dict__[field] is None:
            if self.__annotations__[field] == str:
                setattr(self, field, "")
            if self.__annotations__[field] == Optional[str]:
                setattr(self, field, "")
            elif self.__annotations__[field] == List:
                setattr(self, field, [])
            elif self.__annotations__[field] == Optional[List]:
                setattr(self, field, [])
            elif self.__annotations__[field] == dict:
                setattr(self, field, {})
            else:
                setattr(self, field, None)


def get_bool_value(iterated_form_obj, user_selected_option_id):
    return iterated_form_obj.dropdown_field.options[user_selected_option_id - 1].value


def get_value(column_name, form_obj):
    """Iterates the form object and extracts the required values on the basis of column_name"""
    for i in range(0, len(form_obj.sections)):
        # The above loop will iterate the 'sections' parameter of the json body
        for j in range(0, len(form_obj.sections[i].fields)):
            # The above loop will iterate the 'fields' parameter of the json body
            for k in range(0, len(form_obj.sections[i].fields[j].row_fields)):
                # The above loop will iterate the 'row_fields' parameter of the json body
                if form_obj.sections[i].fields[j].row_fields[k].column_name == column_name:

                    if form_obj.sections[i].fields[j].row_fields[k].field_type == FormTypeEnum.textField:
                        return form_obj.sections[i].fields[j].row_fields[k].user_selection.text_value

                    elif form_obj.sections[i].fields[j].row_fields[k].field_type == FormTypeEnum.datePicker:
                        return form_obj.sections[i].fields[j].row_fields[k].user_selection.user_selected_date

                    else:
                        return get_bool_value(form_obj.sections[i].fields[j].row_fields[
                                                  k], form_obj.sections[i].fields[j].row_fields[
                                                  k].user_selection.user_selected_option_id)

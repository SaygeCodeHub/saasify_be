from datetime import date
from typing import List, Optional, Union, Any

from pydantic import BaseModel

from app.enums.button_action_enum import ButtonActionEnum
from app.enums.button_type_enum import ButtonTypeEnum
from app.enums.form_type_enum import FormTypeEnum


class UserSelection(BaseModel):
    text_value: Optional[str] = None
    user_selected_value: Optional[Union[int, str, float, bool, Any]] = None
    user_selected_date: Optional[date] = None


class DropdownOption(BaseModel):
    label: str
    value: Union[int, str, float, bool, Any]


class DropdownField(BaseModel):
    options: List[DropdownOption]
    default_value: Optional[Union[int, str, float, bool, Any]] = None


class RadioOption(BaseModel):
    label: str
    value: Union[int, str, float, bool, Any]


class RadioField(BaseModel):
    options: List[RadioOption]


class CheckboxOption(BaseModel):
    label: str
    value: Union[int, str, float, bool, Any]
    checked: Optional[bool] = False


class CheckboxField(BaseModel):
    options: List[CheckboxOption]


class DatePickerField(BaseModel):
    placeholder: Optional[str] = None
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    validator: Optional[str] = 'Please fill the empty field'


class TextField(BaseModel):
    max_lines: Optional[int]
    max_length: Optional[int] = None
    obscure_text: Optional[bool] = False
    read_only: Optional[bool] = False
    input_type: Optional[str]
    validator: Optional[str] = 'Please fill the empty field'


class FormField(BaseModel):
    column_name: str
    label: str
    field_type: FormTypeEnum
    placeholder: Optional[str] = None
    required: bool
    error_text: Optional[str] = None
    user_selection: UserSelection = None
    text_field: Optional[TextField] = None
    dropdown_field: Optional[DropdownField] = None
    radio_field: Optional[RadioField] = None
    checkbox_field: Optional[CheckboxField] = None
    date_picker_field: Optional[DatePickerField] = None


class MultifieldsInRow(BaseModel):
    fields: List[FormField]


class SectionWiseForm(BaseModel):
    section_name: Optional[str] = None
    row: List[MultifieldsInRow]


class UtilityButtons(BaseModel):
    button_icon: Optional[str] = None
    end_point: Optional[str] = None
    button_action: ButtonActionEnum = ButtonActionEnum.api_call
    api_method_type: Optional[str] = None


class FormButtons(BaseModel):
    button_name: str
    button_type: Optional[ButtonTypeEnum] = ButtonTypeEnum.primaryButton
    end_point: str
    button_action: ButtonActionEnum = ButtonActionEnum.api_call
    api_method_type: str


class DynamicForm(BaseModel):
    form_name: str
    sections: List[SectionWiseForm]
    buttons: List[FormButtons]
    utility_buttons: List[UtilityButtons] = []

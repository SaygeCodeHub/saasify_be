"""Form type enum"""

from enum import Enum as PyEnum


class FormTypeEnum(PyEnum):
    textField = 'textField'
    dropDown = 'dropDown'
    multipleDropDown = 'multipleDropDown'
    radio = 'radio'
    checkbox = 'checkbox'
    datePicker = 'datePicker'

from app.enums.form_type_enum import FormTypeEnum
from app.enums.leave_type_enum import LeaveType
from app.v3_0.schemas.form_schema import DynamicForm, SectionWiseForm, MultifieldsInRow, FormField, TextField, \
    UserSelection, DatePickerField, FormButtons, DropdownOption, DropdownField


def format_enum_member(enum_member: str):
    return enum_member.capitalize()


def leave_type_dropdown():
    """Format Enums and create options list"""
    dropdown_options = []
    for leave_type in LeaveType:
        dropdown_options.append(
            DropdownOption(label=format_enum_member(leave_type.name), value=leave_type.value))
    return DropdownField(
        options=dropdown_options)


add_leaves = DynamicForm(
    form_name="Apply Leave",
    buttons=[FormButtons(button_name="Apply Leave",
                         end_point="/addLeave",
                         api_method_type="post")],
    sections=[
        SectionWiseForm(
            section_name=None,
            row=[
                MultifieldsInRow(
                    fields=[
                        FormField(
                            column_name="leave_type",
                            label="Leave Type",
                            field_type=FormTypeEnum.dropDown,
                            required=True,
                            user_selection=UserSelection(text_value=""),
                            dropdown_field=leave_type_dropdown()),
                        FormField(
                            column_name="start_date",
                            label="From Date",
                            field_type=FormTypeEnum.datePicker,
                            required=True,
                            user_selection=UserSelection(user_selected_date=None),
                            date_picker_field=DatePickerField(placeholder="Select date", max_date=None)),
                        FormField(
                            column_name="end_date",
                            label="To Date",
                            field_type=FormTypeEnum.datePicker,
                            required=True,
                            user_selection=UserSelection(user_selected_date=None),
                            date_picker_field=DatePickerField(placeholder="Select date",max_date=None)),
                        FormField(
                            column_name="approvers",
                            label="Approvers",
                            field_type=FormTypeEnum.dropDown,
                            required=True,
                            user_selection=UserSelection()),
                    ]),
                MultifieldsInRow(
                    fields=[
                        FormField(
                            column_name="leave_reason",
                            label="Reason for Leave",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=4, input_type="text"),
                            user_selection=UserSelection())])
            ])
    ]
)

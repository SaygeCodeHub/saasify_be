from datetime import datetime

from app.enums.form_type_enum import FormTypeEnum
from app.v3_0.schemas.form_schema import DynamicForm, SectionWiseForm, MultifieldsInRow, FormField, TextField, \
    UserSelection, FormButtons, UtilityButtons, DatePickerField, DropdownField, DropdownOption

add_employee = DynamicForm(
    form_name="Add Employee",
    buttons=[FormButtons(button_name="Add Employee",
                         end_point="/addEmployee",
                         api_method_type="post")],
    sections=[
        SectionWiseForm(
            section_name="Personal Details",
            fields=[
                MultifieldsInRow(
                    row_fields=[
                        FormField(
                            column_name="first_name",
                            label="First Name",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="text", readOnly=False),
                            user_selection=
                            UserSelection(text_value="")),
                        FormField(
                            column_name="middle_name",
                            label="Middle Name",
                            required=False,
                            field_type=FormTypeEnum.textField,
                            text_field=TextField(max_lines=1, input_type="text", readOnly=False),
                            user_selection=
                            UserSelection(text_value="")),
                        FormField(
                            column_name="last_name",
                            label="Last Name",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="text", readOnly=False),
                            user_selection=
                            UserSelection(text_value=""))]),
                MultifieldsInRow(
                    row_fields=[
                        FormField(
                            column_name="user_email",
                            label="Email",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="email", readOnly=False),
                            user_selection=
                            UserSelection(text_value="")),
                        FormField(
                            column_name="user_contact",
                            label="Mobile Number",
                            required=False,
                            field_type=FormTypeEnum.textField,
                            text_field=TextField(max_lines=1, input_type="number", readOnly=False),
                            user_selection=
                            UserSelection(text_value="")),
                        FormField(
                            column_name="alternate_contact",
                            label="Alternate Mobile Number",
                            field_type=FormTypeEnum.textField,
                            required=False,
                            text_field=TextField(max_lines=1, input_type="number", readOnly=False),
                            user_selection=
                            UserSelection(text_value=""))]),
                MultifieldsInRow(
                    row_fields=[
                        FormField(
                            column_name="user_birthdate",
                            label="Date of Birth",
                            field_type=FormTypeEnum.datePicker,
                            required=False,
                            date_picker_field=DatePickerField(min_date="1900-01-01", max_date=datetime.now().date()),
                            user_selection=UserSelection()),
                        FormField(
                            column_name="gender",
                            label="Gender",
                            required=False,
                            field_type=FormTypeEnum.dropDown,
                            dropdown_field=DropdownField(
                                options=[DropdownOption(label="Male", value="Male", option_id=0),
                                         DropdownOption(label="Female", value="Female", option_id=1),
                                         DropdownOption(label="Other", value="Other", option_id=2)]),
                            user_selection=UserSelection()),
                        FormField(
                            column_name="nationality",
                            label="Nationality",
                            field_type=FormTypeEnum.dropDown,
                            required=False,
                            user_selection=UserSelection()),
                        FormField(
                            column_name="marriage_status",
                            label="Marital Status",
                            field_type=FormTypeEnum.dropDown,
                            required=False,
                            user_selection=UserSelection())]),
                MultifieldsInRow(
                    row_fields=[
                        FormField(
                            column_name="current_address",
                            label="Current Address",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="text", readOnly=False),
                            user_selection=
                            UserSelection(text_value="")),
                        FormField(
                            column_name="permanent_address",
                            label="Permanent Address",
                            required=False,
                            field_type=FormTypeEnum.textField,
                            text_field=TextField(max_lines=1, input_type="text", readOnly=False),
                            user_selection=
                            UserSelection(text_value=""))]),
                MultifieldsInRow(
                    row_fields=[FormField(
                        column_name="state",
                        label="State",
                        required=False,
                        field_type=FormTypeEnum.dropDown,
                        user_selection=UserSelection()),
                        FormField(
                            column_name="city",
                            label="City",
                            field_type=FormTypeEnum.dropDown,
                            required=False,
                            user_selection=UserSelection()),
                        FormField(
                            column_name="pincode",
                            label="Pincode",
                            field_type=FormTypeEnum.textField,
                            required=False,
                            user_selection=UserSelection())]),
            ]),
        SectionWiseForm(
            section_name="Document Details",
            fields=[
                MultifieldsInRow(
                    row_fields=[
                        FormField(
                            column_name="first_name",
                            label="First Name",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="text", readOnly=False),
                            user_selection=
                            UserSelection(text_value="")),
                        FormField(
                            column_name="middle_name",
                            label="Middle Name",
                            required=False,
                            field_type=FormTypeEnum.textField,
                            text_field=TextField(max_lines=1, input_type="text", readOnly=False),
                            user_selection=
                            UserSelection(text_value="")),
                        FormField(
                            column_name="last_name",
                            label="Last Name",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="text", readOnly=False),
                            user_selection=
                            UserSelection(text_value=""))]),
                MultifieldsInRow(
                    row_fields=[
                        FormField(
                            column_name="user_email",
                            label="Email",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="email", readOnly=False),
                            user_selection=
                            UserSelection(text_value="")),
                        FormField(
                            column_name="user_contact",
                            label="Mobile Number",
                            required=False,
                            field_type=FormTypeEnum.textField,
                            text_field=TextField(max_lines=1, input_type="number", readOnly=False),
                            user_selection=
                            UserSelection(text_value="")),
                        FormField(
                            column_name="alternate_contact",
                            label="Alternate Mobile Number",
                            field_type=FormTypeEnum.textField,
                            required=False,
                            text_field=TextField(max_lines=1, input_type="number", readOnly=False),
                            user_selection=
                            UserSelection(text_value=""))]),
                MultifieldsInRow(
                    row_fields=[
                        FormField(
                            column_name="user_birthdate",
                            label="Date of Birth",
                            field_type=FormTypeEnum.datePicker,
                            required=False,
                            date_picker_field=DatePickerField(min_date="1900-01-01", max_date=datetime.now().date()),
                            user_selection=UserSelection()),
                        FormField(
                            column_name="gender",
                            label="Gender",
                            required=False,
                            field_type=FormTypeEnum.dropDown,
                            dropdown_field=DropdownField(
                                options=[DropdownOption(label="Male", value="Male", option_id=0),
                                         DropdownOption(label="Female", value="Female", option_id=1),
                                         DropdownOption(label="Other", value="Other", option_id=2)]),
                            user_selection=UserSelection()),
                        FormField(
                            column_name="nationality",
                            label="Nationality",
                            field_type=FormTypeEnum.dropDown,
                            required=False,
                            user_selection=UserSelection()),
                        FormField(
                            column_name="marriage_status",
                            label="Marital Status",
                            field_type=FormTypeEnum.dropDown,
                            required=False,
                            user_selection=UserSelection())]),
                MultifieldsInRow(
                    row_fields=[
                        FormField(
                            column_name="current_address",
                            label="Current Address",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="text", readOnly=False),
                            user_selection=
                            UserSelection(text_value="")),
                        FormField(
                            column_name="permanent_address",
                            label="Permanent Address",
                            required=False,
                            field_type=FormTypeEnum.textField,
                            text_field=TextField(max_lines=1, input_type="text", readOnly=False),
                            user_selection=
                            UserSelection(text_value=""))]),
                MultifieldsInRow(
                    row_fields=[FormField(
                        column_name="state",
                        label="State",
                        required=False,
                        field_type=FormTypeEnum.dropDown,
                        user_selection=UserSelection()),
                        FormField(
                            column_name="city",
                            label="City",
                            field_type=FormTypeEnum.dropDown,
                            required=False,
                            user_selection=UserSelection()),
                        FormField(
                            column_name="pincode",
                            label="Pincode",
                            field_type=FormTypeEnum.dropDown,
                            required=False,
                            user_selection=UserSelection())]),
            ]),

    ]

)

"""Service layer for building forms and tables"""
from app.dto.dto_classes import ResponseDTO
from app.enums.form_type_enum import FormTypeEnum
from app.v3_0.schemas.form_schema import DynamicForm, SectionWiseForm, MultifieldsInRow, FormField, TextField, \
    UserSelection, RadioField, RadioOption, DropdownField, DropdownOption, CheckboxField, CheckboxOption, \
    DatePickerField, FormButtons, UtilityButtons


def plot_announcement_form():
    add_announcements = DynamicForm(
        form_name="Add New Announcements",
        buttons=[FormButtons(button_name="Add Announcement",
                             end_point="/addAnnouncements",
                             api_method_type="post")],
        utility_buttons=[UtilityButtons(button_icon="",
                                        end_point="",
                                        api_method_type=""
                                        )],
        sections=[
            SectionWiseForm(
                section_name=None,
                fields=[MultifieldsInRow(
                    row_fields=[
                        FormField(column_name="due_date", label="Due Date", required=True,
                                  field_type=FormTypeEnum.datePicker,
                                  user_selection=UserSelection(text_value="", date_picker_field=DatePickerField(
                                      placeholder="Select date")
                                                               )),
                        FormField(column_name="is_active",
                                  label="Is Announcement active?",
                                  field_type=FormTypeEnum.dropDown,
                                  required=True,
                                  dropdown_field=DropdownField(
                                      options=[
                                          DropdownOption(
                                              label="Yes", value=1, option_id=1),
                                          DropdownOption(
                                              label="No", value=0, option_id=2)], default_value=True
                                  ), user_selection=UserSelection(
                                user_selected_option_id=None)
                                  )
                    ]),
                    MultifieldsInRow(
                        row_fields=[
                            FormField(column_name="description", label="Description", required=True,
                                      field_type=FormTypeEnum.textField,
                                      text_field=TextField(max_lines=5, input_type="text"),
                                      user_selection=
                                      UserSelection(text_value="",
                                                    date_picker_field=DatePickerField(
                                                        placeholder="Select date")))
                        ])
                ])

        ]

    )

    return ResponseDTO(200, "Form plotted!", add_announcements)

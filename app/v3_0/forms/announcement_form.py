from app.enums.form_type_enum import FormTypeEnum
from app.v3_0.schemas.form_schema import DynamicForm, SectionWiseForm, MultifieldsInRow, FormField, TextField, \
    UserSelection, DatePickerField, FormButtons, UtilityButtons

add_announcements = DynamicForm(
    form_name="Add New Announcement",
    buttons=[FormButtons(button_name="Add Announcement",
                         end_point="/addAnnouncement",
                         api_method_type="post")],

    sections=[
        SectionWiseForm(
            section_name=None,
            fields=[
                MultifieldsInRow(
                    row_fields=[
                        FormField(
                            column_name="due_date",
                            label="Due Date",
                            field_type=FormTypeEnum.datePicker,
                            required=True,
                            user_selection=UserSelection(user_selected_date=None),
                            date_picker_field=DatePickerField(placeholder="Select date", max_date=None))]),
                MultifieldsInRow(
                    row_fields=[
                        FormField(
                            column_name="description",
                            label="Description",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="text"),
                            user_selection=UserSelection(text_value=""))])
            ])
    ]
)

from app.enums.form_type_enum import FormTypeEnum
from app.enums.task_priority_enum import TaskPriority
from app.v3_0.schemas.form_schema import DynamicForm, SectionWiseForm, MultifieldsInRow, FormField, TextField, \
    UserSelection, DatePickerField, FormButtons, DropdownOption, DropdownField


def format_enum_member(enum_member: str):
    return enum_member.capitalize()


def tasks_priority_dropdown():
    """Format Enums and create options list"""
    dropdown_options = []
    for priority in TaskPriority:
        dropdown_options.append(
            DropdownOption(label=format_enum_member(priority.name), value=priority.value))
    return DropdownField(
        options=dropdown_options)


add_tasks = DynamicForm(
    form_name="Add New Task",
    buttons=[FormButtons(button_name="Add Task",
                         end_point="/addTasks",
                         api_method_type="post")],
    sections=[
        SectionWiseForm(
            section_name=None,
            row=[
                MultifieldsInRow(
                    fields=[
                        FormField(
                            column_name="title",
                            label="Title",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="text"),
                            user_selection=UserSelection(text_value="")),
                        FormField(
                            column_name="priority",
                            label="Priority",
                            field_type=FormTypeEnum.dropDown,
                            required=True,
                            dropdown_field=tasks_priority_dropdown(),
                            user_selection=UserSelection()),
                        FormField(
                            column_name="due_date",
                            label="Due Date",
                            field_type=FormTypeEnum.datePicker,
                            required=True,
                            user_selection=UserSelection(user_selected_date=None),
                            date_picker_field=DatePickerField(placeholder="Select date", max_date=None))]),
                MultifieldsInRow(
                    fields=[
                        FormField(
                            column_name="monitored_by",
                            label="Monitored By",
                            field_type=FormTypeEnum.dropDown,
                            required=True,
                            user_selection=UserSelection()),
                        FormField(
                            column_name="assigned_to",
                            label="Assign to",
                            field_type=FormTypeEnum.dropDown,
                            required=True,
                            user_selection=UserSelection())]),
                MultifieldsInRow(
                    fields=[
                        FormField(
                            column_name="task_description",
                            label="Description",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(max_lines=1, input_type="text"),
                            user_selection=UserSelection(text_value=""))])
            ])
    ]
)

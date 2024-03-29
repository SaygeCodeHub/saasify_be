from app.enums.form_type_enum import FormTypeEnum
from app.v3_0.schemas.form_schema import DynamicForm, FormButtons, SectionWiseForm, MultifieldsInRow, \
    FormField, UserSelection, TextField

add_category_form = DynamicForm(
    form_name="Add Category",
    buttons=[FormButtons(button_name="Add Category",
                         end_point="/addCategory",
                         api_method_type="post")],
    sections=[
        SectionWiseForm(
            section_name=None,
            row=[
                MultifieldsInRow(
                    fields=[
                        FormField(
                            column_name="name",
                            label="Name",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(
                                max_lines=1, input_type="text"),
                            user_selection=UserSelection(text_value="")),
                        FormField(column_name="description", label="Description", required=True,
                                  field_type=FormTypeEnum.textField,
                                  text_field=TextField(max_lines=5, input_type="text"),
                                  user_selection=UserSelection())])
            ])
    ]
)

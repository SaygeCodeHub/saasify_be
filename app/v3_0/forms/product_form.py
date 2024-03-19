from app.enums.form_type_enum import FormTypeEnum
from app.v3_0.schemas.form_schema import DynamicForm, FormButtons, SectionWiseForm, MultifieldsInRow, \
    FormField, UserSelection, TextField, DropdownField

add_product_form = DynamicForm(
    form_name="Add Product",
    buttons=[FormButtons(button_name="Add Product",
                         end_point="/addProduct",
                         api_method_type="post")],
    sections=[
        SectionWiseForm(
            section_name=None,
            row=[
                MultifieldsInRow(
                    fields=[
                        FormField(
                            column_name="category_id", label="Category",
                            field_type=FormTypeEnum.dropDown,
                            required=True,
                            user_selection=UserSelection()),
                        FormField(column_name="product_name", label="Product name", required=True,
                                  field_type=FormTypeEnum.textField,
                                  text_field=TextField(max_lines=1, input_type="text"),
                                  user_selection=UserSelection()),
                        FormField(column_name="description", label="Product Description", required=True,
                                  field_type=FormTypeEnum.textField,
                                  text_field=TextField(max_lines=5, input_type="text"),
                                  user_selection=UserSelection()),
                        FormField(column_name="variant_name", label="Variant Name", required=True,
                                  field_type=FormTypeEnum.textField,
                                  text_field=TextField(max_lines=1, input_type="text"),
                                  user_selection=UserSelection()),
                        FormField(column_name="measuring_qty", label="Measuring Quantity", required=True,
                                  field_type=FormTypeEnum.textField,
                                  text_field=TextField(max_lines=1, input_type="text"),
                                  user_selection=UserSelection()),
                        FormField(column_name="stock_qty", label="Stock Quantity", required=True,
                                  field_type=FormTypeEnum.textField,
                                  text_field=TextField(max_lines=1, input_type="text"),
                                  user_selection=UserSelection()),
                    ])
            ])
    ]
)

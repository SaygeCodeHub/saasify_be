from app.enums.form_type_enum import FormTypeEnum
from app.v3_0.schemas.form_schema import DynamicForm, SectionWiseForm, MultifieldsInRow, FormField, TextField, \
    UserSelection, DropdownField, DropdownOption, \
    FormButtons, UtilityButtons

x = 0
y = 0


def get_option_id_for_categories():
    global x
    x = x + 1
    return x


def get_option_id_for_units():
    global y
    y = y + 1
    return y


def send_add_products_form(categories, unit_array):
    add_products_form = DynamicForm(
        form_name="Add New Product",
        buttons=[FormButtons(button_name="Add Product",
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
                        FormField(
                            column_name="product_name",
                            label="Product Name",
                            field_type=FormTypeEnum.textField,
                            required=True,
                            text_field=TextField(
                                max_lines=1, input_type="text"),
                            user_selection=UserSelection(text_value="")
                        ),
                        FormField(column_name="description", label="Description", required=True,
                                  field_type=FormTypeEnum.textField,
                                  text_field=TextField(max_lines=5, input_type="text"),
                                  user_selection=
                                  UserSelection(text_value=""))
                    ]),
                    MultifieldsInRow(
                        row_fields=[
                            FormField(column_name="category_id",
                                      label="Category",
                                      field_type=FormTypeEnum.dropDown,
                                      required=True,
                                      dropdown_field=DropdownField(
                                          options=[
                                              DropdownOption(
                                                  label=category.name, value=category.category_id,
                                                  option_id=get_option_id_for_categories())
                                              for category in categories
                                          ], default_value=None
                                      ), user_selection=UserSelection(
                                    user_selected_option_id=None)
                                      ),
                            FormField(column_name="image", label="Image", required=True,
                                      field_type=FormTypeEnum.textField,
                                      text_field=TextField(max_lines=1, input_type="text"),
                                      user_selection=
                                      UserSelection(text_value=""))
                        ]),
                    MultifieldsInRow(
                        row_fields=[
                            FormField(column_name="measuring_qty", label="Quantity", required=True,
                                      field_type=FormTypeEnum.textField,
                                      text_field=TextField(max_lines=1, input_type="text"),
                                      user_selection=
                                      UserSelection(text_value="")),
                            FormField(column_name="unit",
                                      label="Unit",
                                      field_type=FormTypeEnum.dropDown,
                                      required=True,
                                      dropdown_field=DropdownField(
                                          options=[
                                              DropdownOption(
                                                  label=unit.unit_name, value=unit.unit_name,
                                                  option_id=get_option_id_for_units())
                                              for unit in unit_array
                                          ], default_value=None
                                      ), user_selection=UserSelection(
                                    user_selected_option_id=None)
                                      ),
                            FormField(column_name="price", label="Price", required=True,
                                      field_type=FormTypeEnum.textField,
                                      text_field=TextField(max_lines=1, input_type="text"),
                                      user_selection=
                                      UserSelection(text_value=""))
                        ]
                    ),
                    MultifieldsInRow(
                        row_fields=[
                            FormField(column_name="stock_qty", label="Stock quantity", required=True,
                                      field_type=FormTypeEnum.textField,
                                      text_field=TextField(max_lines=1, input_type="text"),
                                      user_selection=
                                      UserSelection(text_value=""))
                        ]
                    )
                ])

        ]

    )

    global x
    x = 0
    global y
    y = 0

    return add_products_form

# from app.enums.form_type_enum import FormTypeEnum
# from app.v3_0.schemas.form_schema import DynamicForm, SectionWiseForm, MultifieldsInRow, FormField, TextField, \
#     UserSelection, DatePickerField, FormButtons, UtilityButtons
#
# add_employee = DynamicForm(
#     form_name="Add New Announcements",
#     buttons=[FormButtons(button_name="Add Employee",
#                          end_point="/addEmployee",
#                          api_method_type="post")],
#     utility_buttons=[UtilityButtons(button_icon="",
#                                     end_point="",
#                                     api_method_type=""
#                                     )],
#     sections=[
#         SectionWiseForm(
#             section_name=None,
#             fields=[
#                 MultifieldsInRow(
#                     row_fields=[
#                         FormField(
#                             column_name="first_name",
#                             label="First Name",
#                             field_type=FormTypeEnum.textField,
#                             required=True,
#                             text_field=TextField(max_lines=1, input_type="text"),
#                             user_selection=
#                             UserSelection(text_value="")),
#                         FormField(
#                             column_name="middle_name",
#                             label="Middle Name",
#                             required=False,
#                             field_type=FormTypeEnum.textField,
#                             text_field=TextField(max_lines=1, input_type="text"),
#                             user_selection=
#                             UserSelection(text_value="")),
#                         FormField(
#                             column_name="last_name",
#                             label="Last Name",
#                             field_type=FormTypeEnum.textField,
#                             required=True,
#                             text_field=TextField(max_lines=1, input_type="text"),
#                             user_selection=
#                             UserSelection(text_value=""))]),
#                 MultifieldsInRow(
#                     row_fields=[
#                         FormField(
#                             column_name="user_email",
#                             label="Email",
#                             field_type=FormTypeEnum.textField,
#                             required=True,
#                             text_field=TextField(max_lines=1, input_type="email"),
#                             user_selection=
#                             UserSelection(text_value="")),
#                         FormField(
#                             column_name="user_contact",
#                             label="Mobile Number",
#                             required=False,
#                             field_type=FormTypeEnum.textField,
#                             text_field=TextField(max_lines=1, input_type="text"),
#                             user_selection=
#                             UserSelection(text_value="")),
#                         FormField(
#                             column_name="last_name",
#                             label="Last Name",
#                             field_type=FormTypeEnum.textField,
#                             required=True,
#                             text_field=TextField(max_lines=1, input_type="text"),
#                             user_selection=
#                             UserSelection(text_value=""))])
#             ])
#
#     ]
#
# )

null = None
true = True
false = False
bosdy = {
    "status": 200,
    "message": "Form Structure Fetched Successfully",
    "data": {
        "form_name": "Add Employee",
        "sections": [
            {
                "section_name": "Personal Details",
                "row": [
                    {
                        "fields": [
                            {
                                "column_name": "first_name",
                                "label": "First Name",
                                "field_type": "textField",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": {
                                    "max_lines": 1,
                                    "max_length": null,
                                    "obscure_text": false,
                                    "readOnly": false,
                                    "input_type": "text",
                                    "validator": "Please fill the empty field"
                                },
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": null
                            },
                            {
                                "column_name": "middle_name",
                                "label": "Middle Name",
                                "field_type": "textField",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": {
                                    "max_lines": 1,
                                    "max_length": null,
                                    "obscure_text": false,
                                    "readOnly": false,
                                    "input_type": "text",
                                    "validator": "Please fill the empty field"
                                },
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": null
                            },
                            {
                                "column_name": "last_name",
                                "label": "Last Name",
                                "field_type": "textField",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": {
                                    "max_lines": 1,
                                    "max_length": null,
                                    "obscure_text": false,
                                    "readOnly": false,
                                    "input_type": "text",
                                    "validator": "Please fill the empty field"
                                },
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": null
                            }
                        ]
                    },
                    {
                        "fields": [
                            {
                                "column_name": "email_address",
                                "label": "Email Address",
                                "field_type": "textField",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": {
                                    "max_lines": 1,
                                    "max_length": null,
                                    "obscure_text": false,
                                    "readOnly": false,
                                    "input_type": "text",
                                    "validator": "Please fill the empty field"
                                },
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": null
                            },
                            {
                                "column_name": "phone_number",
                                "label": "Phone Number",
                                "field_type": "textField",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": {
                                    "max_lines": 1,
                                    "max_length": null,
                                    "obscure_text": false,
                                    "readOnly": false,
                                    "input_type": "text",
                                    "validator": "Please fill the empty field"
                                },
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": null
                            }
                        ]
                    },
                    {
                        "fields": [
                            {
                                "column_name": "date_of_birth",
                                "label": "Date of Birth",
                                "field_type": "datePicker",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": null,
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": {
                                    "initial_date": null,
                                    "first_date": "1900-01-01",
                                    "last_date": "2022-12-31",
                                    "validator": "Please fill the empty field"
                                }
                            },
                            {
                                "column_name": "gender",
                                "label": "Gender",
                                "field_type": "radio",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": null,
                                "dropdown_field": null,
                                "radio_field": {
                                    "default_value": null,
                                    "options": [
                                        {
                                            "optionId": 1,
                                            "value": "Male",
                                            "label": "Male"
                                        },
                                        {
                                            "optionId": 2,
                                            "value": "Female",
                                            "label": "Female"
                                        },
                                        {
                                            "optionId": 3,
                                            "value": "Other",
                                            "label": "Other"
                                        }
                                    ]
                                },
                                "checkbox_field": null,
                                "date_picker_field": null
                            }
                        ]
                    },
                    {
                        "fields": [
                            {
                                "column_name": "address",
                                "label": "Address",
                                "field_type": "textField",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": {
                                    "max_lines": 5,
                                    "max_length": null,
                                    "obscure_text": false,
                                    "readOnly": false,
                                    "input_type": "text",
                                    "validator": "Please fill the empty field"
                                },
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": null
                            }
                        ]
                    }
                ]
            },
            {
                "section_name": "Document Details",
                "row": [
                    {
                        "fields": [
                            {
                                "column_name": "aadhar_no",
                                "label": "Aadhar No.",
                                "field_type": "textField",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": {
                                    "max_lines": 1,
                                    "max_length": null,
                                    "obscure_text": false,
                                    "readOnly": false,
                                    "input_type": "text",
                                    "validator": "Please fill the empty field"
                                },
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": null
                            },
                            {
                                "column_name": "name_as_per_aadhar",
                                "label": "Name as per Aadhar",
                                "field_type": "textField",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": {
                                    "max_lines": 1,
                                    "max_length": null,
                                    "obscure_text": false,
                                    "readOnly": false,
                                    "input_type": "text",
                                    "validator": "Please fill the empty field"
                                },
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": null
                            }
                        ]
                    },
                    {
                        "fields": [
                            {
                                "column_name": "pan_no",
                                "label": "PAN No.",
                                "field_type": "textField",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": {
                                    "max_lines": 1,
                                    "max_length": null,
                                    "obscure_text": false,
                                    "readOnly": false,
                                    "input_type": "text",
                                    "validator": "Please fill the empty field"
                                },
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": null
                            },
                            {
                                "column_name": "name_as_per_pan",
                                "label": "Name as per PAN",
                                "field_type": "textField",
                                "flex": 1,
                                "placeholder": null,
                                "required": true,
                                "error_text": null,
                                "user_selection": {
                                    "text_value": "",
                                    "user_selected_option_id": null,
                                    "user_selected_date": null
                                },
                                "text_field": {
                                    "max_lines": 1,
                                    "max_length": null,
                                    "obscure_text": false,
                                    "readOnly": false,
                                    "input_type": "text",
                                    "validator": "Please fill the empty field"
                                },
                                "dropdown_field": null,
                                "radio_field": null,
                                "checkbox_field": null,
                                "date_picker_field": null
                            }
                        ]
                    }
                ]
            }
        ],
        "buttons": [
            {
                "button_name": "Add Employee",
                "button_action": "api_call",
                "button_type": "primaryButton",
                "end_point": "/addEmployee",
                "api_method_type": "post"
            }
        ],
        "utility_buttons": [
            {
                "button_icon": "close",
                "button_action": "clear",
                "end_point": "",
                "api_method_type": ""
            }
        ]
    }
}

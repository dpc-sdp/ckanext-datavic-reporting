import ckan.plugins.toolkit as tk

import ckanext.datavic_reporting.helpers as helpers
from ckanext.toolbelt.decorators import Collector

validator, get_validators = Collector("datavic_reporting").split()

Invalid = tk.Invalid


@validator
def sub_org_ids(sub_org_ids, context):
    for sub_org in sub_org_ids.split(","):
        # Ignore checking if 'all-sub-organisations' group exists as we know it does not
        if sub_org.lower() == "all-sub-organisations":
            continue
        tk.get_validator("group_id_or_name_exists")(sub_org.strip(), context)
    return sub_org_ids


@validator("frequency_validator")
def frequency_validator(frequency):
    if frequency not in helpers.get_scheduled_report_frequencies():
        raise Invalid("Invalid frequency")
    return frequency


@validator("user_roles_validator")
def user_roles_validator(user_roles, context):
    for user_role in user_roles.split(","):
        tk.get_validator("role_exists")(user_role.strip(), context)
    return user_roles


@validator("emails_validator")
def emails_validator(emails, context):
    for email in emails.split(","):
        tk.get_validator("email_validator")(email.strip(), context)
    return emails


@validator("report_schedule_validator")
def report_schedule_validator(data_dict, context, action="create"):
    errors = {}

    try:
        tk.get_validator("frequency_validator")(data_dict["frequency"])
    except Exception:
        errors["frequency"] = ["Invalid frequency selection"]

    try:
        tk.get_validator("user_roles_validator")(
            data_dict["user_roles"], context
        )
    except Exception:
        errors["user_roles"] = ["Invalid user role selection"]

    try:
        tk.get_validator("emails_validator")(data_dict["emails"], context)
    except Exception:
        errors["emails"] = ["Invalid email entry"]

    return errors if errors else data_dict

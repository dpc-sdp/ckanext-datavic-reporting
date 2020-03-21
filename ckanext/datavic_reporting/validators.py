import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import Invalid


def report_type_validator(report_type):
    if report_type not in ['monthly', 'yearly']:
        raise Invalid('Invalid report_type')
    return report_type


def sub_org_ids_validator(sub_org_ids, context):
    sub_org_ids = sub_org_ids.split(',')
    for sub_org in sub_org_ids:
        toolkit.get_validator('group_id_exists')(sub_org.strip(), context)
    return sub_org_ids


def frequency_validator(frequency):
    if frequency not in ['monthly', 'yearly']:
        raise Invalid('Invalid frequency')
    return frequency


def user_roles_validator(user_roles, context):
    for user_role in user_roles.split(','):
        toolkit.get_validator('role_exists')(user_role.strip(), context)
    return user_roles


def emails_validator(emails, context):
    for email in emails.split(','):
        toolkit.get_validator('email_validator')(email.strip(), context)
    return emails

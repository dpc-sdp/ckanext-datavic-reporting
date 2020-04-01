import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import Invalid
import constants


def report_type_validator(report_type):
    if report_type not in ['general']:
        raise Invalid('Invalid report_type')
    return report_type


def org_id_validator(org_id, context):
    try:
        toolkit.get_validator('group_id_or_name_exists')(org_id, context)
    except Exception:
        raise Invalid('Invalid organisation')
    return org_id


def sub_org_ids_validator(sub_org_ids, context):
    sub_org_ids = sub_org_ids.split(',')
    for sub_org in sub_org_ids:
        toolkit.get_validator('group_id_or_name_exists')(sub_org.strip(), context)
    return sub_org_ids


def frequency_validator(frequency):
    if frequency not in constants.Frequencies.List:
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


def report_schedule_validator(data_dict, context, action='create'):
    errors = {}
    if action == 'create':
        try:
            toolkit.get_validator('report_type_validator')(data_dict['report_type'])
        except Exception:
            errors['report_type'] = [u'Invalid or no report type selected']

        try:
            toolkit.get_validator('org_id_validator')(data_dict['org_id'], context)
        except Exception:
            errors['org_id'] = [u'Invalid or no organisation selected']

        sub_org_ids = data_dict.get('sub_org_ids', '')

        if sub_org_ids:
            try:
                toolkit.get_validator('sub_org_ids_validator')(data_dict['sub_org_ids'], context)
            except Exception:
                errors['sub_org_ids'] = 'Invalid sub-organisation selection'

    try:
        toolkit.get_validator('frequency_validator')(data_dict['frequency'])
    except Exception:
        errors['frequency'] = [u'Invalid frequency selection']

    try:
        toolkit.get_validator('user_roles_validator')(data_dict['user_roles'], context)
    except Exception:
        errors['user_roles'] = [u'Invalid user role selection']

    try:
        toolkit.get_validator('emails_validator')(data_dict['emails'], context)
    except Exception:
        errors['emails'] = [u'Invalid email entry']

    return errors if errors else data_dict


def report_job_validator(data_dict, context):
    errors = {}

    # id = data_dict.get('id', None)
    #
    # # Check to make sure `id` looks like a UUID
    # if id and model.is_id(id):

    return errors if errors else data_dict



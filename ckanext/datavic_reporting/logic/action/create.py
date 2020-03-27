import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckanext.datavic_reporting.report_models import ReportSchedule, ReportJob


def report_schedule_create(context, data_dict):
    errors = {}
    try:
        # Check access - see authorisaton.py for implementation
        toolkit.check_access('report_schedule_create', context, {})

        sub_org_ids = data_dict.get('sub_org_ids', '')

        # Validate data_dict inputs - see validators.py for implementations
        validated_data_dict = toolkit.get_validator('report_schedule_validator')(data_dict, context)

        if validated_data_dict is data_dict:
            schedule_dict = {
                'user_id': toolkit.c.userobj.id,
                'report_type': data_dict['report_type'],
                'org_id': data_dict['org_id'],
                'sub_org_ids': sub_org_ids,
                'frequency': data_dict['frequency'],
                'user_roles': data_dict['user_roles'],
                'emails': data_dict['emails'],
                'state': 'active'
            }
            model.Session.add(ReportSchedule(**schedule_dict))
            model.Session.commit()
            return True
        else:
            errors = validated_data_dict
    except Exception, e:
        errors['exception'] = str(e)

    return {'errors': errors}


def report_job_create(context, data_dict):
    errors = {}
    try:
        validated_data_dict = toolkit.get_validator('report_job_validator')(data_dict, context)

        if validated_data_dict is data_dict:
            report_job_dict = {
                'report_schedule_id': data_dict['report_schedule_id'],
                'filename': data_dict['filename'],
                'status': 'scheduled'
            }
            model.Session.add(ReportJob(**report_job_dict))
            model.Session.commit()
            return True
        else:
            errors = validated_data_dict
    except Exception, e:
        errors['exception'] = str(e)

    return {'errors': errors}

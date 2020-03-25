import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckanext.datavic_reporting.report_models import ReportSchedule


def report_schedule_create(context, data_dict):
    try:
        # Check access - see authorisaton.py for implementation
        toolkit.check_access('report_schedule_create', context, {})

        # Validate data_dict inputs - see validators.py for implementations
        toolkit.get_validator('report_type_validator')(data_dict['report_type'])
        toolkit.get_validator('org_id_validator')(data_dict['org_id'], context)
        from pprint import pprint
        pprint(data_dict)

        sub_org_ids = data_dict.get('sub_org_ids', '')

        if sub_org_ids:
            toolkit.get_validator('sub_org_ids_validator')(data_dict['sub_org_ids'], context)

        toolkit.get_validator('frequency_validator')(data_dict['frequency'])
        toolkit.get_validator('user_roles_validator')(data_dict['user_roles'], context)
        toolkit.get_validator('emails_validator')(data_dict['emails'], context)

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
    except Exception, e:
        return {'error': str(e)}

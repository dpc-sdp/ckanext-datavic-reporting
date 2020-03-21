import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckanext.datavic_reporting.report_models import ReportSchedule


def report_schedule_update(context, data_dict):
    error = 'Invalid or no report schedule ID provided.'

    id = data_dict.get('id', None)

    # Check to make sure `id` looks like a UUID
    if id and model.is_id(id):
        try:
            # Check access - see authorisaton.py for implementation
            toolkit.check_access('report_schedule_update', context, {})

            # Load the record
            schedule = ReportSchedule.get(id)
            if schedule:
                # The list of fields that can be updated is controlled here
                for field in ['report_type', 'org_id', 'sub_org_ids', 'frequency', 'user_roles', 'emails']:
                    value = data_dict.get(field, None)
                    if value:
                        setattr(schedule, field, value)

                # Validate data_dict inputs - see validators.py for implementations
                toolkit.get_validator('report_type_validator')(schedule.report_type)
                toolkit.get_validator('group_id_exists')(schedule.org_id, context)
                toolkit.get_validator('sub_org_ids_validator')(schedule.sub_org_ids, context)
                toolkit.get_validator('frequency_validator')(schedule.frequency)
                toolkit.get_validator('user_roles_validator')(schedule.user_roles, context)
                toolkit.get_validator('emails_validator')(schedule.emails, context)

                model.Session.add(schedule)
                model.Session.commit()
                return True
        except Exception, e:
            error = str(e)

    return {'error': error}

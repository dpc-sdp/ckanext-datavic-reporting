import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckanext.datavic_reporting.report_models import ReportSchedule


def report_schedule_update(context, data_dict):
    errors = {}

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
                for field in ['frequency', 'user_roles', 'emails']:
                    value = data_dict.get(field, None)
                    if value:
                        setattr(schedule, field, value)

                # Validate data_dict inputs - see validators.py for implementations
                validated_data_dict = toolkit.get_validator('report_schedule_validator')(data_dict, context, 'update')

                if validated_data_dict is data_dict:
                    model.Session.add(schedule)
                    model.Session.commit()
                    return True
                else:
                    errors = validated_data_dict
        except Exception as e:
            errors['exception'] = str(e)
    else:
        errors = 'Invalid or no report schedule ID provided.'

    return {'errors': errors}

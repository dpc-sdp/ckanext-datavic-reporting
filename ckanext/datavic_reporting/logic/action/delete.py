import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckanext.datavic_reporting.report_models import ReportSchedule
from ckan.logic import side_effect_free


@side_effect_free
def report_schedule_delete(context, data_dict):
    error = 'Invalid or no report schedule ID provided.'

    id = data_dict.get('id', None)

    # Check to make sure `id` looks like a UUID
    if id and model.is_id(id):
        try:
            toolkit.check_access('report_schedule_delete', context, {'id': id})

            # Load the record
            schedule = ReportSchedule.get(id)
            if schedule:
                # Mark it as deleted
                schedule.state = 'deleted'
                # Save
                model.Session.add(schedule)
                model.Session.commit()
                return True
        except Exception, e:
            error = str(e)

    return {'error': error}

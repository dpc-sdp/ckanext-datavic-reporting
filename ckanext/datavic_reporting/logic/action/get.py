import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckanext.datavic_reporting.report_models import ReportSchedule, ReportJob
from ckan.logic import side_effect_free


@side_effect_free
def report_schedule_list(context, data_dict):
    state = data_dict.get('state', None)
    try:
        # Check access - see authorisaton.py for implementation
        toolkit.check_access('report_schedule_list', context, {})
        if state:
            scheduled_reports = model.Session.query(ReportSchedule).filter_by(state=state).all()
        else:
            scheduled_reports = model.Session.query(ReportSchedule).all()
        return [s.as_dict() for s in scheduled_reports]
    except Exception, e:
        return {'error': str(e)}


@side_effect_free
def reports_list(context, data_dict):
    error = 'Invalid or no report schedule ID provided.'

    id = data_dict.get('id', None)

    # Check to make sure `id` looks like a UUID
    if id and model.is_id(id):
        try:
            # Check access - see authorisaton.py for implementation
            toolkit.check_access('reports_list', context, {})
            reports = model.Session.query(ReportJob).filter_by(report_schedule_id=id).all()
            return [r.as_dict() for r in reports]
        except Exception, e:
            error = str(e)

    return {'error': error}

import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckanext.datavic_reporting.report_models import ReportSchedule, ReportJob
from ckan.logic import side_effect_free


@side_effect_free
def report_schedule_list(context, data_dict):
    state = data_dict.get('state', None)
    frequency = data_dict.get('frequency', None)
    try:
        # Check access - see authorisaton.py for implementation
        toolkit.check_access('report_schedule_list', context, {})
        if state and frequency:
            scheduled_reports = model.Session.query(ReportSchedule)\
                                                .filter_by(state=state)\
                                                .filter_by(frequency=frequency)\
                                                .all()
        elif state:
            scheduled_reports = model.Session.query(ReportSchedule).filter_by(state=state).all()
        else:
            scheduled_reports = model.Session.query(ReportSchedule).all()
        return [s.as_dict() for s in scheduled_reports]
    except Exception, e:
        return {'error': str(e)}


@side_effect_free
def report_jobs(context, data_dict):
    error = 'Invalid or no report schedule ID provided.'

    report_schedule_id = data_dict.get('report_schedule_id', None)

    # Check to make sure `id` looks like a UUID
    if report_schedule_id and model.is_id(report_schedule_id):
        try:
            # Check access - see authorisaton.py for implementation
            toolkit.check_access('report_jobs', context, {})
            report_jobs = model.Session.query(ReportJob).filter_by(report_schedule_id=report_schedule_id).all()
            return [r.as_dict() for r in report_jobs]
        except Exception, e:
            error = str(e)

    return {'error': error}

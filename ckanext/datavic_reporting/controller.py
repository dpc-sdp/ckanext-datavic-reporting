import ckan.lib.base as base
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.controllers.api import ApiController
from ckanext.datavic_reporting.report_models import ReportSchedule
from pylons import response
from datetime import datetime
import json
import helpers
import authorisation

request = base.request


class ReportingController(base.BaseController):
    @classmethod
    def check_user_access(cls):
        user_dashboard_reports = authorisation.user_dashboard_reports(helpers.get_context())
        if not user_dashboard_reports or not user_dashboard_reports.get('success'):
            toolkit.NotAuthorized(403, toolkit._('You are not Authorized'))

    @classmethod
    def general_report(cls, start_date, end_date, organisation):
        # Generate a CSV report
        filename = 'general_report_{0}.csv'.format(datetime.now().isoformat())
        helpers.generate_general_report(filename, start_date, end_date, organisation)

        return cls.download_csv(filename)

    @classmethod
    def download_csv(cls, filename):
        fh = open('/tmp/' + filename)

        response.headers[b'Content-Type'] = b'text/csv; charset=utf-8'
        response.headers[b'Content-Disposition'] = b"attachment;filename=%s" % filename

        return fh.read()

    def reports(self):
        self.check_user_access()
        vars = {}

        return base.render('user/reports.html',
                           extra_vars=vars)

    def reports_general_year_month(self):
        self.check_user_access()

        year, month = helpers.get_year_month(
            toolkit.request.GET.get('report_date_year', None),
            toolkit.request.GET.get('report_date_month', None)
        )

        start_date, end_date = helpers.get_report_date_range(year, month)
        organisation = toolkit.request.GET.get('organisation', None)
        sub_organisation = toolkit.request.GET.get('sub_organisation', 'all-sub-organisations')

        return self.general_report(start_date, end_date, organisation if sub_organisation == 'all-sub-organisations' else sub_organisation)

    def reports_general_date_range(self):
        self.check_user_access()

        start_date = toolkit.request.GET.get('report_date_from', None)
        end_date = toolkit.request.GET.get('report_date_to', None)
        organisation = toolkit.request.GET.get('organisation', None)
        sub_organisation = toolkit.request.GET.get('sub_organisation', 'all-sub-organisations')

        return self.general_report(start_date, end_date, organisation if sub_organisation == 'all-sub-organisations' else sub_organisation)

    def reports_sub_organisations(self):
        self.check_user_access()

        organisation_id = toolkit.request.GET.get('organisation_id', None)

        return json.dumps(helpers.get_organisation_node_tree(organisation_id))


class ScheduledReportController(base.BaseController):
    def create(self):
        response = 'Error'
        if request.method == 'POST':
            params = helpers.clean_params(request.POST)

            # @TODO: Validate POST inputs

            schedule_dict = {
                'user_id': toolkit.c.userobj.id,
                'report_type': params['report_type'],
                'org_id': params['org_id'],
                'sub_org_ids': params['sub_org_ids'],
                'frequency': params['frequency'],
                'user_roles': params['user_roles'],
                'emails': params['emails'],
                'state': 'active'
            }

            try:
                model.Session.add(ReportSchedule(**schedule_dict))
                model.Session.commit()

                response = 'OK - create'
            except Exception, e:
                response = str(e)

        return ApiController()._finish_ok(response)

    def update(self, id=None):
        response = 'Error'
        if request.method == 'POST' and id and model.is_id(id):
            params = helpers.clean_params(request.POST)
            try:
                # Load the record
                schedule = ReportSchedule.get(id)
                if schedule:
                    # The list of fields that can be updated is controlled here
                    for field in ['report_type', 'org_id', 'sub_org_ids', 'frequency', 'user_roles', 'emails']:
                        value = params.get(field, None)
                        if value:
                            setattr(schedule, field, value)
                    model.Session.add(schedule)
                    model.Session.commit()
                    response = 'OK - update'
            except Exception, e:
                response = str(e)

        return ApiController()._finish_ok(response)

    def delete(self, id=None):
        '''
        Delete a report_schedule record by ID
        :param id:
        :return:
        '''
        response = 'Error'

        # Check to make sure `id` looks like a UUID
        if id and model.is_id(id):
            try:
                # Load the record
                schedule = ReportSchedule.get(id)
                # Mark it as deleted
                schedule.state = 'deleted'
                # Save
                model.Session.add(schedule)
                model.Session.commit()
                response = 'OK - is an id'
            except Exception, e:
                response = str(e)

        return ApiController()._finish_ok(response)

    def list(self):
        '''
        Only returns the `report_schedule` records with state = 'active'
        :return:
        '''
        scheduled_reports = model.Session.query(ReportSchedule).filter_by(state='active').all()
        return ApiController()._finish_ok([s.as_dict() for s in scheduled_reports])

    def reports(self, scheduled_report_id):
        return ApiController()._finish_ok('OK - reports')

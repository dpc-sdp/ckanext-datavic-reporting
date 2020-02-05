import ckan.lib.base as base
import ckan.authz as authz
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import helpers
from pylons import response
from ckan.common import _
from datetime import datetime
import json

abort = base.abort


class ReportingController(base.BaseController):
    @classmethod
    def check_sysadmin_access(cls):
        # Only sysadmin users can generate reports
        user = toolkit.c.userobj
        if not user or not authz.is_sysadmin(user.name):
            abort(403, _('You are not permitted to perform this action.'))

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
        self.check_sysadmin_access()
        vars = {}

        return base.render('user/reports.html',
                           extra_vars=vars)

    def reports_general_year_month(self):
        self.check_sysadmin_access()

        year, month = helpers.get_year_month(
            toolkit.request.GET.get('report_date_year', None),
            toolkit.request.GET.get('report_date_month', None)
        )

        start_date, end_date = helpers.get_report_date_range(year, month)
        organisation = toolkit.request.GET.get('organisation', None)
        sub_organisation = toolkit.request.GET.get('sub_organisation', None)

        return self.general_report(start_date, end_date, sub_organisation or organisation)

    def reports_general_date_range(self):
        self.check_sysadmin_access()

        start_date = toolkit.request.GET.get('report_date_from', None)
        end_date = toolkit.request.GET.get('report_date_to', None)
        organisation = toolkit.request.GET.get('organisation', None)
        sub_organisation = toolkit.request.GET.get('sub_organisation', None)

        return self.general_report(start_date, end_date, sub_organisation or organisation)

    def reports_sub_organisations(self):
        self.check_sysadmin_access()

        organisation_id = toolkit.request.GET.get('organisation_id', None)

        return json.dumps(helpers.get_organisation_node_tree(organisation_id))

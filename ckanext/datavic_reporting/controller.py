import ckan.lib.base as base
import ckan.authz as authz
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import helpers
from pylons import response
from ckan.common import _
from datetime import datetime

abort = base.abort


class ReportingController(base.BaseController):
    @classmethod
    def check_sysadmin_access(cls):
        # Only sysadmin users can generate reports
        user = toolkit.c.userobj
        if not user or not authz.is_sysadmin(user.name):
            abort(403, _('You are not permitted to perform this action.'))

    @classmethod
    def general_report(cls, start_date, end_date):

        # Generate a CSV report
        filename = 'general_report_{0}.csv'.format(datetime.now().isoformat())
        helpers.generate_general_report(filename, start_date, end_date)

        return cls.download_csv(filename)

    @classmethod
    def download_csv(cls, filename):
        fh = open('/tmp/' + filename)

        response.headers[b'Content-Type'] = b'text/csv; charset=utf-8'
        response.headers[b'Content-Disposition'] = b"attachment;filename=%s" % filename

        return fh.read()

    def reports_general_year_month(self):
        self.check_sysadmin_access()

        year, month = helpers.get_year_month(
            toolkit.request.GET.get('report_date_year', None),
            toolkit.request.GET.get('report_date_month', None)
        )

        start_date, end_date = helpers.get_report_date_range(year, month)

        return self.general_report(start_date, end_date)

    def reports_general_date_range(self):
        self.check_sysadmin_access()

        start_date = toolkit.request.GET.get('report_date_from', None)
        end_date = toolkit.request.GET.get('report_date_to', None)

        return self.general_report(start_date, end_date)


class ReportingAdminController(base.BaseController):
    def admin(self):
        vars = {}

        return base.render('admin/reports.html',
                           extra_vars=vars)

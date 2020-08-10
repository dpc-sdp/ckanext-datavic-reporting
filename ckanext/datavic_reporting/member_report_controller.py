import ckan.lib.base as base
import ckan.plugins.toolkit as toolkit
from datetime import datetime
import helpers
import authorisation

abort = base.abort


class MemberReportController(base.BaseController):
    @classmethod
    def check_user_access(cls):
        user_dashboard_reports = authorisation.user_dashboard_reports(helpers.get_context())
        if not user_dashboard_reports or not user_dashboard_reports.get('success'):
            abort(403, toolkit._('You are not Authorized'))

    @classmethod
    def download_report(self):
        # Generate a CSV report
        path = '/tmp/'
        filename = 'member_report_{0}.csv'.format(datetime.now().isoformat())
        file_path = path + filename
        helpers.generate_member_report(path, filename)

        return helpers.download_file(file_path)

    def report(self):
        self.check_user_access()
        vars = {
            'members': toolkit.get_action('organisation_members')({}, {})
        }

        return base.render('member/report.html',
                           extra_vars=vars)

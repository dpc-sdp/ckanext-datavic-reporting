import ckan.lib.base as base
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.controllers.api import ApiController
from ckanext.datavic_reporting.report_models import ReportSchedule, ReportJob
from pylons import response
from datetime import datetime
import os
import json
import helpers
import authorisation
import constants

c = toolkit.c
h = base.h
request = base.request
abort = base.abort


# class ReportingController(base.BaseController):
#     @classmethod
#     def check_user_access(cls):
#         user_dashboard_reports = authorisation.user_dashboard_reports(helpers.get_context())
#         if not user_dashboard_reports or not user_dashboard_reports.get('success'):
#             abort(403, toolkit._('You are not Authorized'))

#     @classmethod
#     def general_report(cls, start_date, end_date, organisation):
#         # Generate a CSV report
#         path = '/tmp/'
#         filename = 'general_report_{0}.csv'.format(datetime.now().isoformat())
#         file_path = path + filename
#         helpers.generate_general_report(path, filename, start_date, end_date, organisation)

#         return helpers.download_file(file_path)

#     def reports(self):
#         self.check_user_access()
#         vars = {}

#         return base.render('user/reports.html',
#                            extra_vars=vars)

#     def reports_general_year_month(self):
#         self.check_user_access()

#         year, month = helpers.get_year_month(
#             toolkit.request.GET.get('report_date_year', None),
#             toolkit.request.GET.get('report_date_month', None)
#         )

#         start_date, end_date = helpers.get_report_date_range(year, month)
#         organisation = toolkit.request.GET.get('organisation', None)
#         sub_organisation = toolkit.request.GET.get('sub_organisation', 'all-sub-organisations')

#         return self.general_report(start_date, end_date, organisation if sub_organisation == 'all-sub-organisations' else sub_organisation)

#     def reports_general_date_range(self):
#         self.check_user_access()

#         start_date = toolkit.request.GET.get('report_date_from', None)
#         end_date = toolkit.request.GET.get('report_date_to', None)
#         organisation = toolkit.request.GET.get('organisation', None)
#         sub_organisation = toolkit.request.GET.get('sub_organisation', 'all-sub-organisations')

#         return self.general_report(start_date, end_date, organisation if sub_organisation == 'all-sub-organisations' else sub_organisation)

#     def reports_sub_organisations(self):
#         self.check_user_access()

#         organisation_id = toolkit.request.GET.get('organisation_id', None)

#         return json.dumps(helpers.get_organisation_node_tree(organisation_id))


# class ReportScheduleController(base.BaseController):
#     @classmethod
#     def check_user_access(cls):
#         user_report_schedules = authorisation.user_report_schedules(helpers.get_context())
#         if not user_report_schedules or not user_report_schedules.get('success'):
#             abort(403, toolkit._('You are not Authorized'))

#     def schedules(self):
#         self.check_user_access()

#         vars = {}

#         return base.render('user/report_schedules.html',
#                            extra_vars=vars)

    # def create(self):
    #     self.check_user_access()

    #     vars = {}
    #     if request.method == 'POST':
    #         params = helpers.clean_params(request.POST)
    #         result = toolkit.get_action('report_schedule_create')(helpers.get_context(), params)
    #         # handle success
    #         if result is True:
    #             h.flash_success('Report schedule created')
    #             h.redirect_to('/dashboard/report-schedules')
    #         # handle errors
    #         elif result and result.get('errors', None):
    #             vars['data'] = params
    #             vars['errors'] = result.get('errors', None)
    #             h.flash_error('Please correct the errors below')

    #     return base.render('user/report_schedules.html',
    #                        extra_vars=vars)

    # def update(self, id):
    #     self.check_user_access()

    #     vars = {}
    #     if request.method == 'GET':
    #         if id and model.is_id(id):
    #             schedule = ReportSchedule.get(id)
    #             if schedule:
    #                 vars['data'] = schedule.as_dict()
    #     elif request.method == 'POST':
    #         params = helpers.clean_params(request.POST)
    #         params['id'] = id
    #         result = toolkit.get_action('report_schedule_update')(helpers.get_context(), params)
    #         if result is True:
    #             h.flash_success('Report schedule updated')
    #             h.redirect_to('/dashboard/report-schedules')
    #         elif result and result.get('errors', None):
    #             vars['data'] = params
    #             vars['errors'] = result.get('errors', None)
    #             h.flash_error('Please correct the errors below')

    #     return base.render('user/report_schedules.html',
    #                        extra_vars=vars)

    # def delete(self, id=None):
    #     self.check_user_access()

    #     result = toolkit.get_action('report_schedule_delete')(helpers.get_context(), {'id': id})
    #     if result is True:
    #         h.flash_success('Report schedule deleted')
    #     else:
    #         h.flash_error('Error deleting report schedule')
    #     h.redirect_to('/dashboard/report-schedules')

    # def jobs(self, report_schedule_id=None):
    #     self.check_user_access()

    #     vars = {}

    #     schedule = ReportSchedule.get(report_schedule_id)
    #     if schedule:
    #         vars['schedule'] = schedule.as_dict()
    #         vars['jobs'] = toolkit.get_action('report_jobs')(helpers.get_context(), {'report_schedule_id': report_schedule_id})

    #     return base.render('user/report_jobs.html', extra_vars=vars)

    # def job_download(self, report_job_id=None):
    #     self.check_user_access()
        
    #     job = ReportJob.get(report_job_id)
    #     if job:
    #        return helpers.download_file(job.filename)
    #     else:
    #         h.flash_error('Error: Could not find job file to download')

import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import helpers
import authorisation
import logging
import validators

log = logging.getLogger(__name__)


class DataVicReportingPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IAuthFunctions)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IActions, inherit=True)
    p.implements(p.IValidators, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datavic_reporting')

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'user_dashboard_reports': authorisation.user_dashboard_reports,
            'report_schedule_create': authorisation.report_schedule_create,
            'report_schedule_update': authorisation.report_schedule_update,
            'report_schedule_delete': authorisation.report_schedule_delete,
            'report_schedule_list': authorisation.report_schedule_list,
            'report_jobs': authorisation.report_jobs,
        }

    # IRoutes
    def before_map(self, map):
        # Reporting mappings
        map.connect('user_dashboard_reports', '/dashboard/reports',
                    controller='ckanext.datavic_reporting.controller:ReportingController',
                    action='reports',
                    ckan_icon='file')
        map.connect('user_reports_general_year_month', '/user/reports/general_year_month',
                    controller='ckanext.datavic_reporting.controller:ReportingController',
                    action='reports_general_year_month')
        map.connect('user_reports_general_date_range', '/user/reports/general_date_range',
                    controller='ckanext.datavic_reporting.controller:ReportingController',
                    action='reports_general_date_range')
        map.connect('user_reports_sub_organisations', '/user/reports/sub_organisations',
                    controller='ckanext.datavic_reporting.controller:ReportingController',
                    action='reports_sub_organisations')

        # Scheduled reports
        map.connect('user_report_schedules', '/dashboard/report-schedules',
                    controller='ckanext.datavic_reporting.controller:ReportScheduleController',
                    action='schedules',
                    ckan_icon='file')
        map.connect('user_report_schedule_create', '/dashboard/report-schedule/create',
                    controller='ckanext.datavic_reporting.controller:ReportScheduleController',
                    action='create')
        map.connect('user_report_schedule_update', '/dashboard/report-schedule/update/{id}',
                    controller='ckanext.datavic_reporting.controller:ReportScheduleController',
                    action='update')
        map.connect('user_report_schedule_delete', '/dashboard/report-schedule/delete/{id}',
                    controller='ckanext.datavic_reporting.controller:ReportScheduleController',
                    action='delete')
        map.connect('user_report_schedule_jobs', '/dashboard/report-schedule/jobs/{report_schedule_id}',
                    controller='ckanext.datavic_reporting.controller:ReportScheduleController',
                    action='jobs')
        map.connect('user_report_schedule_job_download', '/dashboard/report-schedule/jobs/{report_job_id}/download',
                    controller='ckanext.datavic_reporting.controller:ReportScheduleController',
                    action='job_download')

        return map

    # ITemplateHelpers
    def get_helpers(self):
        ''' Return a dict of named helper functions (as defined in the ITemplateHelpers interface).
        These helpers will be available under the 'h' thread-local global object.
        '''
        return {
            'user_report_get_years': helpers.user_report_get_years,
            'user_report_get_months': helpers.user_report_get_months,
            'user_report_get_organisations': helpers.get_organisation_list,
            'get_report_schedules': helpers.get_report_schedules,
            'get_report_schedule_organisation_list': helpers.get_report_schedule_organisation_list,
        }

    # IActions
    def get_actions(self):
        from ckanext.datavic_reporting.logic.action import create, update, delete, get

        return {
            "report_schedule_create": create.report_schedule_create,
            "report_schedule_update": update.report_schedule_update,
            "report_schedule_delete": delete.report_schedule_delete,
            "report_schedule_list": get.report_schedule_list,
            "report_jobs": get.report_jobs,
            "report_job_create": create.report_job_create,
        }

    # IValidators
    def get_validators(self):
        return {
            "report_type_validator": validators.report_type_validator,
            "org_id_validator": validators.org_id_validator,
            "sub_org_ids_validator": validators.sub_org_ids_validator,
            "frequency_validator": validators.frequency_validator,
            "user_roles_validator": validators.user_roles_validator,
            "emails_validator": validators.emails_validator,
            "report_schedule_validator": validators.report_schedule_validator,
            "report_job_validator": validators.report_job_validator,
        }


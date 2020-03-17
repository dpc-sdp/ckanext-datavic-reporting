import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import helpers
import authorisation
import logging

log = logging.getLogger(__name__)


class DataVicReportingPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IAuthFunctions)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datavic_reporting')

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'user_dashboard_reports': authorisation.user_dashboard_reports,
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
        # Scheduled report mappings
        map.connect('scheduled_report_create', '/user/scheduled_report/create',
                    controller='ckanext.datavic_reporting.controller:ScheduledReportController',
                    action='create')
        map.connect('scheduled_report_update', '/user/scheduled_report/update/{id}',
                    controller='ckanext.datavic_reporting.controller:ScheduledReportController',
                    action='update')
        map.connect('scheduled_report_delete', '/user/scheduled_report/delete/{id}',
                    controller='ckanext.datavic_reporting.controller:ScheduledReportController',
                    action='delete')
        map.connect('scheduled_report_list', '/user/scheduled_report/list',
                    controller='ckanext.datavic_reporting.controller:ScheduledReportController',
                    action='list')
        map.connect('scheduled_report_reports', '/user/scheduled_report/reports/{id}',
                    controller='ckanext.datavic_reporting.controller:ScheduledReportController',
                    action='reports')

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
        }

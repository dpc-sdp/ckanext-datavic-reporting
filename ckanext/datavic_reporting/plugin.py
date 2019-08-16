import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import helpers


class DataVicReportingPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datavic-reporting')
        toolkit.add_ckan_admin_tab(config_, 'ckanadmin_reports', 'Reports')

    # IRoutes
    def before_map(self, map):
        # Reporting mappings
        map.connect('ckanadmin_reports', '/ckan-admin/reports',
                    controller='ckanext.datavic_reporting.controller:ReportingAdminController', action='admin')
        map.connect('ckanadmin_reports_general_year_month', '/ckan-admin/reports/general_year_month',
                    controller='ckanext.datavic_reporting.controller:ReportingController', action='reports_general_year_month')
        map.connect('ckanadmin_reports_general_date_range', '/ckan-admin/reports/general_date_range',
                    controller='ckanext.datavic_reporting.controller:ReportingController', action='reports_general_date_range')
        return map

    def get_helpers(self):
        ''' Return a dict of named helper functions (as defined in the ITemplateHelpers interface).
        These helpers will be available under the 'h' thread-local global object.
        '''
        return {
            'admin_report_get_years': helpers.admin_report_get_years,
            'admin_report_get_months': helpers.admin_report_get_months,
        }

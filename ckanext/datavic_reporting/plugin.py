import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import logging
import ckanext.datavic_reporting.helpers as helpers
import ckanext.datavic_reporting.authorisation as authorisation
import ckanext.datavic_reporting.validators as validators

from ckanext.datavic_reporting.cli import get_commands

log = logging.getLogger(__name__)


class DataVicReportingPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IAuthFunctions)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IActions, inherit=True)
    p.implements(p.IValidators, inherit=True)
    p.implements(p.IClick)
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return helpers._register_blueprints()

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datavic_reporting')

    ## IConfigurer interface
    def update_config_schema(self, schema):
        schema.update({
            'ckan.datavic_reporting.scheduled_reporting_frequencies': [
                toolkit.get_validator('ignore_missing'),
                str
            ]
        })

        return schema

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'user_dashboard_reports': authorisation.user_dashboard_reports,
            'user_report_schedules': authorisation.user_report_schedules,
            'report_schedule_create': authorisation.report_schedule_create,
            'report_schedule_update': authorisation.report_schedule_update,
            'report_schedule_delete': authorisation.report_schedule_delete,
            'report_schedule_list': authorisation.report_schedule_list,
            'report_jobs': authorisation.report_jobs,
        }

    # IRoutes
    ## TODO: Remove after validating blueprint rutes work
    # def before_map(self, map):
       
    #     return map

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
            'get_scheduled_report_frequencies_list': helpers.get_scheduled_report_frequencies_list,
            'display_member_state': helpers.display_member_state,
            'get_organisation_node_tree': helpers.get_organisation_node_tree,
            'get_user_states': helpers.get_user_states,
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
            "organisation_members": get.organisation_members,
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

    # IClick
    def get_commands(self):
        return get_commands()


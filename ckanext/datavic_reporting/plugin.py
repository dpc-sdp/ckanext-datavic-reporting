import logging

import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.datavic_reporting.helpers as helpers
from ckanext.datavic_reporting.cli import get_commands

from . import views
from .logic import action, auth, validators

log = logging.getLogger(__name__)


class DataVicReportingPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IAuthFunctions)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IActions)
    p.implements(p.IValidators)
    p.implements(p.IClick)
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return views.get_blueprints()

    # IConfigurer
    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")
        tk.add_resource("assets", "datavic_reporting")

    def update_config_schema(self, schema):
        schema.update(
            {
                "ckan.datavic_reporting.scheduled_reporting_frequencies": [
                    tk.get_validator("ignore_missing"),
                    tk.get_validator("unicode_safe"),
                ]
            }
        )

        return schema

    # IAuthFunctions
    def get_auth_functions(self):
        return auth.get_auth_functions()

    # ITemplateHelpers
    def get_helpers(self):
        """Return a dict of named helper functions (as defined in the ITemplateHelpers interface).
        These helpers will be available under the 'h' thread-local global object.
        """
        return {
            "user_report_get_years": helpers.user_report_get_years,
            "user_report_get_months": helpers.user_report_get_months,
            "user_report_get_organisations": helpers.get_organisation_list,
            "get_report_schedules": helpers.get_report_schedules,
            "get_report_schedule_organisation_list": helpers.get_report_schedule_organisation_list,
            "get_scheduled_report_frequencies_list": helpers.get_scheduled_report_frequencies_list,
            "display_member_state": helpers.display_member_state,
            "get_organisation_node_tree": helpers.get_organisation_node_tree,
            "get_user_states": helpers.get_user_states,
        }

    # IActions
    def get_actions(self):
        return action.get_actions()

    # IValidators
    def get_validators(self):
        return validators.get_validators()

    # IClick
    def get_commands(self):
        return get_commands()

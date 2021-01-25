# encoding: utf-8
import logging
import json

from flask import Blueprint
from datetime import datetime


import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
from ckan.common import _, g, request
import ckan.plugins.toolkit as toolkit


import ckanext.datavic_reporting.helpers as helpers
import ckanext.datavic_reporting.authorisation as authorisation
import ckanext.datavic_reporting.validators as validators

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
#TemplateNotFound = logic.TemplateNotFound
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key


render = base.render
abort = base.abort

log = logging.getLogger(__name__)

reporting = Blueprint('reporting', __name__)


@reporting.before_request
def _check_user_access():
    user_dashboard_reports = authorisation.user_dashboard_reports(helpers.get_context())
    if not user_dashboard_reports or not user_dashboard_reports.get('success'):
        abort(403, toolkit._('You are not Authorized'))

def _general_report(start_date, end_date, organisation):
    # Generate a CSV report
    path = '/tmp/'
    filename = 'general_report_{0}.csv'.format(datetime.now().isoformat())
    file_path = path + filename
    helpers.generate_general_report(path, filename, start_date, end_date, organisation)

    return helpers.download_file(file_path)


def reports():
    _check_user_access()
    vars = {}

    return render('user/reports.html', extra_vars=vars)

def reports_general_year_month():
    _check_user_access()

    year, month = helpers.get_year_month(
        toolkit.request.GET.get('report_date_year', None),
        toolkit.request.GET.get('report_date_month', None)
    )

    start_date, end_date = helpers.get_report_date_range(year, month)
    organisation = toolkit.request.GET.get('organisation', None)
    sub_organisation = toolkit.request.GET.get('sub_organisation', 'all-sub-organisations')

    return _general_report(start_date, end_date, organisation if sub_organisation == 'all-sub-organisations' else sub_organisation)

def reports_general_date_range():
    _check_user_access()

    start_date = toolkit.request.GET.get('report_date_from', None)
    end_date = toolkit.request.GET.get('report_date_to', None)
    organisation = toolkit.request.GET.get('organisation', None)
    sub_organisation = toolkit.request.GET.get('sub_organisation', 'all-sub-organisations')

    return _general_report(start_date, end_date, organisation if sub_organisation == 'all-sub-organisations' else sub_organisation)

def reports_sub_organisations():
    _check_user_access()

    organisation_id = toolkit.request.GET.get('organisation_id', None)

    return json.dumps(helpers.get_organisation_node_tree(organisation_id))


def register_datavic_reporting_plugin_rules(blueprint):
    blueprint.add_url_rule('/dashboard/reports', view_func=reports)
    blueprint.add_url_rule('/user/reports/general_year_month', view_func=reports_general_year_month)
    blueprint.add_url_rule('/user/reports/general_date_range', view_func=reports_general_date_range)
    blueprint.add_url_rule('/user/reports/sub_organisations', view_func=reports_sub_organisations)

register_datavic_reporting_plugin_rules(reporting)

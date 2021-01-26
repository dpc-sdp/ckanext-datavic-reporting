
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

member_report = Blueprint('member_report', __name__)


@member_report.before_request
def check_user_access():
    user_dashboard_reports = authorisation.user_dashboard_reports(helpers.get_context())
    if not user_dashboard_reports or not user_dashboard_reports.get('success'):
        abort(403, toolkit._('You are not Authorized'))


def download_report(data_dict):
    # Generate a CSV report
    path = '/tmp/'
    filename = 'member_report_{0}.csv'.format(datetime.now().isoformat())
    file_path = path + filename

    helpers.generate_member_report(path, filename, data_dict)

    return helpers.download_file(file_path)

def extract_request_params():
    organisation = toolkit.request.GET.get('organisation', None)
    sub_organisation = toolkit.request.GET.get('sub_organisation', 'all-sub-organisations')

    data_dict = {
        'organisation': organisation,
        'organisations': None,
        'report_title': toolkit._('All organisations'),
        'state': toolkit.request.GET.get('state', None),
        'sub_organisation': sub_organisation,
    }

    if organisation:
        if sub_organisation == 'all-sub-organisations':
            # Get the organisation and all sub-organisation names
            data_dict['organisations'] = helpers.get_organisation_children_names(organisation)
            if organisation != 'all-organisations':
                data_dict['report_title'] = helpers.get_organisation(organisation).title
        else:
            sub_org_info = helpers.get_organisation(sub_organisation)
            data_dict['organisations'] = [
                sub_org_info.name
            ]
            data_dict['report_title'] = sub_org_info.title

    return data_dict

def report():
    data_dict = extract_request_params()

    view = toolkit.request.GET.get('view', 'display')

    if view == 'download':
        # return self.download_report(organisations)
        return download_report(data_dict)
    else:
        if data_dict['organisation']:
            data_dict['members'] = toolkit.get_action('organisation_members')({}, data_dict)

    return base.render('member/report.html', extra_vars=data_dict)

def register_member_report_plugin_rules(blueprint):
    blueprint.add_url_rule('/dashboard/member_report', view_func=report)

register_member_report_plugin_rules(member_report)

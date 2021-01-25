import logging
import json

from flask import Blueprint
from flask.views import MethodView

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
from ckanext.datavic_reporting.report_models import ReportSchedule, ReportJob


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

scheduling = Blueprint('scheduling', __name__)

@scheduling.before_request
def _check_user_access():
        user_report_schedules = authorisation.user_report_schedules(helpers.get_context())
        if not user_report_schedules or not user_report_schedules.get('success'):
            abort(403, toolkit._('You are not Authorized'))

def schedules():
    _check_user_access()

    vars = {}

    return base.render('user/report_schedules.html',
                        extra_vars=vars)


#TODO: use _check_user_access as before request
class ReportSchedulingCreate(MethodView):

    def get(self):
        vars = {}
        return render('user/report_schedules.html', extra_vars=vars)

    def post(self):
        params = helpers.clean_params(request.POST)
        result = toolkit.get_action('report_schedule_create')(helpers.get_context(), params)
        # handle success
        if result is True:
            h.flash_success('Report schedule created')
            h.redirect_to('/dashboard/report-schedules')
        # handle errors
        elif result and result.get('errors', None):
            vars['data'] = params
            vars['errors'] = result.get('errors', None)
            h.flash_error('Please correct the errors below')



class ReportSchedulingUpdate(MethodView):

    def get(self):
        if id and model.is_id(id):
            schedule = ReportSchedule.get(id)
            if schedule:
                vars['data'] = schedule.as_dict()
        return render('user/report_schedules.html', extra_vars=vars)

    def post(self):
        params = helpers.clean_params(request.POST)
        params['id'] = id
        result = toolkit.get_action('report_schedule_update')(helpers.get_context(), params)
        if result is True:
            h.flash_success('Report schedule updated')
            h.redirect_to('/dashboard/report-schedules')
        elif result and result.get('errors', None):
            vars['data'] = params
            vars['errors'] = result.get('errors', None)
            h.flash_error('Please correct the errors below')


class ReportSchedulingDelete(MethodView):

    def post(self):
        result = toolkit.get_action('report_schedule_delete')(helpers.get_context(), {'id': id})
        if result is True:
            h.flash_success('Report schedule deleted')
        else:
            h.flash_error('Error deleting report schedule')
        h.redirect_to('/dashboard/report-schedules')


#TODO: Add route rules
def register_datavic_scheduling_plugin_rules(blueprint):
    blueprint.add_url_rule('/dashboard/report-schedules', view_func=schedules)
    # blueprint.add_url_rule('/user/reports/general_year_month', view_func=reports_general_year_month)
    # blueprint.add_url_rule('/user/reports/general_date_range', view_func=reports_general_date_range)
    # blueprint.add_url_rule('/user/reports/sub_organisations', view_func=reports_sub_organisations)

register_datavic_scheduling_plugin_rules(scheduling)
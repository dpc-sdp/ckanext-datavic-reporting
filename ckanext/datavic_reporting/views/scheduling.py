import logging
import json

from flask import Blueprint
from flask.views import MethodView

from datetime import datetime


import ckan.lib.helpers as h
import ckan.model as model
from ckan.common import _, g, request
import ckan.plugins.toolkit as toolkit


import ckanext.datavic_reporting.helpers as helpers
import ckanext.datavic_reporting.authorisation as authorisation
import ckanext.datavic_reporting.validators as validators
from ckanext.datavic_reporting.report_models import ReportSchedule, ReportJob


get_action = toolkit.get_action


render = toolkit.render
abort = toolkit.abort

log = logging.getLogger(__name__)

scheduling = Blueprint('scheduling', __name__)

@scheduling.before_request
def _check_user_access():
    user_report_schedules = authorisation.user_report_schedules(helpers.get_context())
    if not user_report_schedules or not user_report_schedules.get('success'):
        abort(403, toolkit._('You are not Authorized'))


def schedules():
    vars = {}
    return render('user/report_schedules.html', extra_vars=vars)

def jobs(report_schedule_id=None):
    '''
    Jobs endpoint
    '''
    vars = {}
    schedule = ReportSchedule.get(report_schedule_id)
    if schedule:
        vars['schedule'] = schedule.as_dict()
        vars['jobs'] = toolkit.get_action('report_jobs')(helpers.get_context(), {'report_schedule_id': report_schedule_id})

    return render('user/report_jobs.html', extra_vars=vars)

def job_download(report_job_id=None):
    '''
    Jobs download
    '''
    job = ReportJob.get(report_job_id)
    if job:
        return helpers.download_file(job.filename)
    else:
        h.flash_error('Error: Could not find job file to download')


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


def register_datavic_scheduling_plugin_rules(blueprint):
    blueprint.add_url_rule('/dashboard/report-schedules', view_func=schedules)
    blueprint.add_url_rule('/dashboard/report-schedule/create', view_func=ReportSchedulingCreate.as_view(str('create')))
    blueprint.add_url_rule('/dashboard/report-schedule/update', view_func=ReportSchedulingUpdate.as_view(str('update')))
    blueprint.add_url_rule('/dashboard/report-schedule/delete', view_func=ReportSchedulingDelete.as_view(str('delete')))
    blueprint.add_url_rule('/dashboard/report-schedule/jobs/<report_schedule_id>', view_func=jobs)
    blueprint.add_url_rule('/dashboard/report-schedule/jobs/<report_job_id>/download', view_func=job_download)

register_datavic_scheduling_plugin_rules(scheduling)
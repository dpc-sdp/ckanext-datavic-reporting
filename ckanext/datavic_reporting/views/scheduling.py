import logging
import os

import ckan.model as model
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from flask.views import MethodView

import ckanext.datavic_reporting.helpers as helpers
from ckanext.datavic_reporting.model import ReportJob, ReportSchedule

from ..logic import auth

get_action = toolkit.get_action
h = toolkit.h
_ = toolkit._

render = toolkit.render
abort = toolkit.abort

log = logging.getLogger(__name__)

scheduling = Blueprint("scheduling", __name__)


@scheduling.before_request
def _check_user_access():
    user_report_schedules = auth.user_report_schedules(helpers.get_context())
    if not user_report_schedules or not user_report_schedules.get("success"):
        abort(403, toolkit._("You are not Authorized"))


def schedules():
    extra_vars = helpers.setup_extra_template_variables()
    return render("user/report_schedules.html", extra_vars=extra_vars)


def jobs(id=None):
    """
    Jobs endpoint
    """
    extra_vars = helpers.setup_extra_template_variables()
    schedule = ReportSchedule.get(id)
    if schedule:
        extra_vars["schedule"] = schedule.as_dict()
        extra_vars["jobs"] = toolkit.get_action("datavic_reporting_job_list")(
            helpers.get_context(), {"report_schedule_id": id}
        )

    return render("user/report_jobs.html", extra_vars=extra_vars)


def job_download(id=None):
    """
    Jobs download
    """
    extra_vars = helpers.setup_extra_template_variables()
    job = ReportJob.get(id)
    if job:
        directory = os.path.dirname(job.filename)
        filename = os.path.basename(job.filename)
        return helpers.download_file(directory, filename)
    else:
        h.flash_error("Error: Could not find job file to download")

    return render("user/report_jobs.html", extra_vars=extra_vars)


class ReportSchedulingCreate(MethodView):
    def get(self):
        extra_vars = helpers.setup_extra_template_variables()
        return render("user/report_schedules.html", extra_vars=extra_vars)

    def post(self):
        params = helpers.clean_params(toolkit.request.form)
        try:
            toolkit.get_action("datavic_reporting_schedule_create")(
                helpers.get_context(), params
            )
        except toolkit.ValidationError as e:
            extra_vars = helpers.setup_extra_template_variables()
            extra_vars["data"] = params
            extra_vars["errors"] = e.error_dict
            h.flash_error("Please correct the errors below")
            return render("user/report_schedules.html", extra_vars=extra_vars)

        h.flash_success("Report schedule created")
        return h.redirect_to("scheduling.schedules")


class ReportSchedulingUpdate(MethodView):
    def get(self, id):
        extra_vars = helpers.setup_extra_template_variables()
        if id and model.is_id(id):
            schedule = ReportSchedule.get(id)
            if schedule:
                extra_vars["data"] = schedule.as_dict()
        return render("user/report_schedules.html", extra_vars=extra_vars)

    def post(self, id):
        params = helpers.clean_params(toolkit.request.form)
        params["id"] = id
        result = toolkit.get_action("datavic_reporting_schedule_update")(
            helpers.get_context(), params
        )
        if result is True:
            h.flash_success("Report schedule updated")
            return h.redirect_to("scheduling.schedules")
        elif result and result.get("errors", None):
            extra_vars = helpers.setup_extra_template_variables()
            extra_vars["data"] = params
            extra_vars["errors"] = result.get("errors", None)
            h.flash_error("Please correct the errors below")
            return render("user/report_schedules.html", extra_vars=extra_vars)


class ReportSchedulingDelete(MethodView):
    def get(self, id):
        try:
            toolkit.get_action("datavic_reporting_schedule_delete")(
                helpers.get_context(), {"id": id}
            )
        except (toolkit.ValidationError, toolkit.ObjectNotFound):
            h.flash_error("Error deleting report schedule")
        else:
            h.flash_success("Report schedule deleted")

        return h.redirect_to("scheduling.schedules")


def register_datavic_scheduling_plugin_rules(blueprint):
    blueprint.add_url_rule("/dashboard/report-schedules", view_func=schedules)
    blueprint.add_url_rule(
        "/dashboard/report-schedule/create",
        view_func=ReportSchedulingCreate.as_view(str("create")),
    )
    blueprint.add_url_rule(
        "/dashboard/report-schedule/update/<id>",
        view_func=ReportSchedulingUpdate.as_view(str("update")),
    )
    blueprint.add_url_rule(
        "/dashboard/report-schedule/delete/<id>",
        view_func=ReportSchedulingDelete.as_view(str("delete")),
    )
    blueprint.add_url_rule(
        "/dashboard/report-schedule/jobs/<id>", view_func=jobs
    )
    blueprint.add_url_rule(
        "/dashboard/report-schedule/job/<id>/download", view_func=job_download
    )


register_datavic_scheduling_plugin_rules(scheduling)

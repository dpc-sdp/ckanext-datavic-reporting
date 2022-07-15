# encoding: utf-8
import json
import logging
import calendar
from datetime import datetime

import ckan.plugins.toolkit as toolkit
from ckan.common import _
from flask import Blueprint

from .. import helpers
from ..logic import auth

get_action = toolkit.get_action


render = toolkit.render
abort = toolkit.abort

log = logging.getLogger(__name__)

reporting = Blueprint("reporting", __name__)


@reporting.before_request
def _check_user_access():
    user_dashboard_reports = auth.user_dashboard_reports(helpers.get_context())
    if not user_dashboard_reports or not user_dashboard_reports.get("success"):
        abort(403, toolkit._("You are not Authorized"))


def _general_report(start_date, end_date, organisation):
    # Generate a CSV report
    directory = "/tmp/"
    filename = "general_report_{0}.csv".format(datetime.now().isoformat())

    helpers.generate_general_report(
        directory, filename, start_date, end_date, organisation
    )

    return helpers.download_file(directory, filename)


def reports():
    extra_vars = helpers.setup_extra_template_variables()

    return render("user/reports.html", extra_vars=extra_vars)


def _get_year_month(year, month):
    now = datetime.now()

    if not year:
        year = now.year

    if not month:
        month = now.month

    return int(year), int(month)


def reports_general_year_month():
    year, month = _get_year_month(
        toolkit.request.args.get("report_date_year", None),
        toolkit.request.args.get("report_date_month", None),
    )

    start_date, end_date = _get_report_date_range(year, month)
    organisation = toolkit.request.args.get("organisation", None)
    sub_organisation = toolkit.request.args.get(
        "sub_organisation", "all-sub-organisations"
    )

    return _general_report(
        start_date,
        end_date,
        organisation
        if sub_organisation == "all-sub-organisations"
        else sub_organisation,
    )


def _get_report_date_range(year, month):
    month_range = calendar.monthrange(year, month)

    start_date = datetime(year, month, 1).strftime("%Y-%m-%d")
    end_date = datetime(year, month, month_range[1]).strftime("%Y-%m-%d")

    return start_date, end_date


def reports_general_date_range():
    start_date = toolkit.request.args.get("report_date_from", None)
    end_date = toolkit.request.args.get("report_date_to", None)
    organisation = toolkit.request.args.get("organisation", None)
    sub_organisation = toolkit.request.args.get(
        "sub_organisation", "all-sub-organisations"
    )

    return _general_report(
        start_date,
        end_date,
        organisation
        if sub_organisation == "all-sub-organisations"
        else sub_organisation,
    )


def reports_sub_organisations():
    organisation_id = toolkit.request.args.get("organisation_id", None)

    return json.dumps(helpers.organisation_tree(organisation_id))


def register_datavic_reporting_plugin_rules(blueprint):
    blueprint.add_url_rule("/dashboard/reports", view_func=reports)
    blueprint.add_url_rule(
        "/user/reports/general_year_month",
        view_func=reports_general_year_month,
    )
    blueprint.add_url_rule(
        "/user/reports/general_date_range",
        view_func=reports_general_date_range,
    )
    blueprint.add_url_rule(
        "/user/reports/sub_organisations", view_func=reports_sub_organisations
    )


register_datavic_reporting_plugin_rules(reporting)

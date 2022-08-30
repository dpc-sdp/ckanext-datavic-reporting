# encoding: utf-8

import logging
from datetime import datetime

import ckan.plugins.toolkit as toolkit
from ckan.common import _
from flask import Blueprint

import ckanext.datavic_reporting.helpers as helpers

from ..logic import auth

get_action = toolkit.get_action


render = toolkit.render
abort = toolkit.abort

log = logging.getLogger(__name__)

member_report = Blueprint("member_report", __name__)


@member_report.before_request
def check_user_access():
    user_dashboard_reports = auth.user_dashboard_reports(helpers.get_context())
    if not user_dashboard_reports or not user_dashboard_reports.get("success"):
        abort(403, toolkit._("You are not Authorized"))


def download_report(data_dict):
    # Generate a CSV report
    directory = "/tmp/"
    filename = "member_report_{0}.csv".format(datetime.now().isoformat())

    helpers.generate_member_report(directory, filename, data_dict)

    return helpers.download_file(directory, filename)


def extract_request_params():
    organisation = toolkit.request.args.get("organisation", None)
    sub_organisation = toolkit.request.args.get(
        "sub_organisation", "all-sub-organisations"
    )

    data_dict = {
        "organisation": organisation,
        "organisations": None,
        "report_title": toolkit._("All organisations"),
        "state": toolkit.request.args.get("state", None),
        "sub_organisation": sub_organisation,
    }
    extra_vars = helpers.setup_extra_template_variables()
    data_dict.update(extra_vars)

    if organisation:
        if sub_organisation == "all-sub-organisations":
            # Get the organisation and all sub-organisation names
            data_dict[
                "organisations"
            ] = helpers.get_organisation_children_names(organisation)
            if organisation != "all-organisations":
                data_dict["report_title"] = helpers.get_organisation(
                    organisation
                ).title
        else:
            sub_org_info = helpers.get_organisation(sub_organisation)
            data_dict["organisations"] = [sub_org_info.name]
            data_dict["report_title"] = sub_org_info.title

    return data_dict


def report():
    data_dict = extract_request_params()

    view = toolkit.request.args.get("view", "display")

    if view == "download":
        # return self.download_report(organisations)
        return download_report(data_dict)
    else:
        if data_dict["organisation"]:
            data_dict["members"] = toolkit.get_action(
                "datavic_reporting_organisation_members"
            )({}, data_dict)

    return render("member/report.html", extra_vars=data_dict)


def register_member_report_plugin_rules(blueprint):
    blueprint.add_url_rule("/dashboard/member_report", view_func=report)


register_member_report_plugin_rules(member_report)

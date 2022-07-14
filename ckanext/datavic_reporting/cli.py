# -*- coding: utf-8 -*-

import ckan.model as model
import ckan.plugins.toolkit as tk
import click

from ckanext.datavic_reporting import constants


@click.group(name="datavic_reporting", short_help="Manage reporting commands")
def reporting():
    """Manage reporting commands"""
    pass


@reporting.command("createjob")
@click.argument("frequency", required=True)
@click.pass_context
def create_scheduled_report_job(ctx, frequency):
    """Create a scheduled report job"""
    click.secho("Running  create_scheduled_report_job", fg="green")
    click.secho("Frequency: {0}".format(frequency), fg="green")

    if not frequency:
        tk.error_shout(
            "You must specify the scheduled report state eg. Monthly or Yearly"
        )
        return

    user = tk.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}

    with ctx.meta["flask_app"].test_request_context():
        # This needs to be set for the helpers.get_username() and helpers.get_user()
        tk.g.user = user["name"]
        tk.g.userobj = model.User.get(user["name"])

        try:
            result = tk.get_action("datavic_reporting_schedule_list")(
                context,
                data_dict={
                    "state": constants.States.Active,
                    "frequency": frequency,
                },
            )
            for report_schedule in result:
                # Generate a CSV report
                tk.get_action("datavic_reporting_job_create")(
                    context, data_dict=report_schedule
                )
        except Exception as ex:
            tk.error_shout(
                "Error running scheduled report frequency {0}".format(
                    frequency
                )
            )
            tk.error_shout("Error: {0}".format(ex))


def get_commands():
    return [reporting]

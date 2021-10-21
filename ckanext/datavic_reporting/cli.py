# -*- coding: utf-8 -*-

import click
import ckan.plugins.toolkit as tk
import ckan.model as model

from ckanext.datavic_reporting import report_models, constants


@click.group(name=u'datavic_reporting', short_help=u'Manage reporting commands')
def reporting():
    """Example of group of commands.
    """
    pass


@reporting.command(u"initdb")
def init_db_cmd():
    """Initialise the database tables required for internal reporting
    """
    click.secho(u"Initializing reporting tables", fg=u"green")

    try:
        report_models.init_tables()
    except Exception as e:
        tk.error_shout(str(e))

    click.secho(u"Reporting DB tables are setup", fg=u"green")


@reporting.command(u"createjob")
@click.argument(u"frequency", required=True)
@click.pass_context
def create_scheduled_report_job(ctx, frequency):
    """Create a scheduled report job
    """
    click.secho(u"Running  create_scheduled_report_job", fg=u"green")
    click.secho(u"Frequency: {0}".format(frequency), fg=u"green")

    if not frequency:
        tk.error_shout(u"You must specify the scheduled report state eg. Monthly or Yearly")
        return

    try:
        # Validator does not work for some reason
        # Don't think we need it here though
        # tk.get_validator('frequency_validator')(frequency)
        # We'll need a sysadmin user to perform most of the actions
        # We will use the sysadmin site user (named as the site_id)
        flask_app = ctx.meta['flask_app']
        with flask_app.test_request_context():
            context = {'ignore_auth': True}
            admin_user = tk.get_action('get_site_user')(context, {})
            # This needs to be set for the helpers.get_username() and helpers.get_user()
            tk.g.user = admin_user['name']
            tk.g.userobj = model.User.get(admin_user['name'])
            context['user'] = admin_user['name']

            result = tk.get_action('report_schedule_list')(context, data_dict={"state": constants.States.Active, "frequency": frequency})
            if result.get('success', False) == False:
                raise Exception(result.get('error', None))
            for report_schedule in result.get('result'):
                # Generate a CSV report
                result = tk.get_action('report_job_create')(context, data_dict=report_schedule)
                if result.get('success', False) == False:
                    tk.error_shout("Error creating report job: {0}".format(result.get('error', None)))
    except Exception as ex:
        tk.error_shout("Error running scheduled report frequency {0}".format(frequency))
        tk.error_shout("Error: {0}".format(ex))


def get_commands():
    return [reporting, init_db_cmd, create_scheduled_report_job]

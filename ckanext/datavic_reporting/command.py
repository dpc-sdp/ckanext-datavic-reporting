from ckan.lib.cli import CkanCommand
# No other CKAN imports allowed until _load_config is run,
# or logging is disabled


class InitDB(CkanCommand):
    """Initialise the extension's database tables
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):
        self._load_config()

        import logging
        log = logging.getLogger(__name__)
        import ckan.model as model
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        import report_models
        report_models.init_tables()
        log.info("Reporting DB tables are setup")

class CreateScheduledReportJob(CkanCommand):
    """Create a new scheduled report job
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 1
    min_args = 1

    def command(self):
        self._load_config()

        import logging
        log = logging.getLogger(__name__)
        from ckan import model
        from ckan.plugins import toolkit
        import constants     
        import os
        
        if len(self.args) != 1:
            log.error("You must specify the scheduled report state eg. Monthly or Yearly")
            return
        
        frequency = self.args[0].lower()       
        if frequency in constants.Frequencies.List:
            # We'll need a sysadmin user to perform most of the actions
            # We will use the sysadmin site user (named as the site_id)
            context = {'model':model,'session':model.Session,'ignore_auth':True}
            self.admin_user = toolkit.get_action('get_site_user')(context,{})
            context = {
                'model':model,
                'session':model.Session,
                'user': self.admin_user['name'],              
                'ignore_auth': True,
            }
            scheduled_reports = toolkit.get_action('report_schedule_list')(context, data_dict={"state": constants.States.Active, "frequency": frequency})
            for report_schedule in scheduled_reports:
                # Generate a CSV report
                result = toolkit.get_action('report_job_create')(context, data_dict=report_schedule)
                if not result:
                    log.error("Error creating report job: {0}".format(result))
        else:
            log.error("Unknown scheduled report state {0}".format(frequency))
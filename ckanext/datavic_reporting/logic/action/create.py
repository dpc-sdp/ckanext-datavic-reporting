import ckan.model as model
from ckan.plugins import toolkit
from ckanext.datavic_reporting.report_models import ReportSchedule, ReportJob
import datetime
import ckanext.datavic_reporting.helpers as helpers
import ckanext.datavic_reporting.constants as constants
import ckanext.datavic_reporting.mailer as mailer
import logging

log = logging.getLogger(__name__)

def report_schedule_create(context, data_dict):
    errors = {}
    try:
        # Check access - see authorisaton.py for implementation
        toolkit.check_access('report_schedule_create', context, {})

        sub_org_ids = data_dict.get('sub_org_ids', '')

        # Validate data_dict inputs - see validators.py for implementations
        validated_data_dict = toolkit.get_validator('report_schedule_validator')(data_dict, context)

        if validated_data_dict is data_dict:
            schedule_dict = {
                'user_id': toolkit.c.userobj.id,
                'report_type': data_dict['report_type'],
                'org_id': data_dict['org_id'],
                'sub_org_ids': sub_org_ids,
                'frequency': data_dict['frequency'],
                'user_roles': data_dict['user_roles'],
                'emails': data_dict['emails'],
                'state': 'active'
            }
            model.Session.add(ReportSchedule(**schedule_dict))
            model.Session.commit()
            return True
        else:
            errors = validated_data_dict
    except Exception, e:
        errors['exception'] = str(e)

    return {'errors': errors}


def report_job_create(context, data_dict):
    errors = {}
    try:
        validated_data_dict = toolkit.get_validator('report_job_validator')(data_dict, context)

        if validated_data_dict is data_dict:
            report_job_path = toolkit.config.get('ckan.datavic_reporting.scheduled_reports_path')
            org_id = data_dict.get('org_id')
            sub_org_ids = data_dict.get('sub_org_ids')
            organisation = org_id if sub_org_ids == 'all-sub-organisations' else sub_org_ids
            now = datetime.datetime.now()
            path_date = now.strftime('%Y') + '/' + now.strftime('%m')
            path = "{0}/{1}/{2}/".format(report_job_path, organisation, path_date)
            filename = 'general_report_{0}.csv'.format(now.isoformat())  
            file_path = path + filename   

            report_job_dict = {
                'report_schedule_id': data_dict['id'],
                'filename': file_path,
                'frequency': data_dict['frequency'],
                'user_roles': data_dict['user_roles'],
                'emails': data_dict['emails'],            
                'status': constants.Statuses.Processing
            }
            report_job = ReportJob(**report_job_dict)
            model.Session.add(report_job)
            model.Session.commit()

            helpers.generate_general_report(path, filename, None, None, organisation)
           
            report_job.status = constants.Statuses.Generated
            model.Session.commit()

            user_emails = [] 
            if data_dict.get('user_roles'):               
                for user_role in data_dict.get('user_roles').split(','):
                    role_emails = helpers.get_organisation_role_emails(context, organisation, user_role)
                    if role_emails:
                        user_emails.append(role_emails)

            if data_dict.get('emails'):
                user_emails.extend(data_dict.get('emails').split(','))          

            if user_emails and len(user_emails) > 0:
                extra_vars = {
                    'site_title': toolkit.config.get('ckan.site_title'),
                    'site_url': toolkit.config.get('ckan.site_url'),
                    'org_id': data_dict.get('org_id'),
                    'frequency': data_dict.get('frequency'),
                    'date': now.strftime('%Y') + ' ' + now.strftime('%B'),
                    'file_path': file_path
                }
                mailer.send_scheduled_report_email(user_emails, 'scheduled_report', extra_vars)
                report_job.status = constants.Statuses.EmailsSent
            else:
                report_job.status = constants.Statuses.NoEmails
                
            model.Session.commit()
            return True
        else:
            errors = validated_data_dict
    except Exception, e:
        report_job.status = constants.Statuses.Failed
        model.Session.commit()
        log.error(e)
        errors['exception'] = str(e)

    return {'errors': errors}
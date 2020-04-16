# ckanext-datavic-reporting
Custom CKAN reporting extension for Data.Vic

### Create Database Tables

This extension utilises two new database tables in the main CKAN database:

__report_schedule:__ stores scheduled report configuration settings.

__report:__ an instance of a report generate via the scheduled report.

Use the following paster command to initialise the tables:

    . /app/ckan/default/bin/activate

    cd /app/src/ckanext-datavic-reporting

    paster initdb --config=/app/ckan/default/production.ini

* Replacing `production.ini` with the respective CKAN .ini file to be used.

### Create scheduled reporting frequencies

The scheduled reporting frequencies list is configurable comma seperated string from the ckan admin config page /ckan-admin/config
Each frequencies is separated by a comma

## Creating Scheduled Report Job

To create the scheduled report job a paster command is used.
The paster command accepts a frequency parameter which used to filter scheduled reports b frequency.
Reports are created for the scheduled report to the file system using the following path and naming conventions
{ckan.datavic_reporting.scheduled_reports_path}/org_id/{yyyy}/{mm}/general_report_{timestamp}.csv

Before running the paster command configure the CKAN .ini file:
ckan.datavic_reporting.scheduled_reports_path = /app/filestore/reports

To run the paster command (Replace {frequency} with 'monthly' or 'yearly'):

    . /app/ckan/default/bin/activate

    cd /app/src/ckanext-datavic-reporting

    paster createjob {frequency} --config=/app/ckan/default/production.ini

## API Endpoints

This extension adds the following endpoints to the standard CKAN API (e.g. http://datavic-ckan.docker.amazee.io/api/action/ACTION_NAME):

### report_schedule_create

__verb:__ POST

__params:__

    report_type - 
    org_id - organisation UUID
    sub_org_ids - comma separated list of sub-org UUIDs
    frequency - 'monthly' or 'yearly'
    user_roles - comma separated list of org roles, e.g. 'admin,editor'
    emails - comma separated list of email addresses

### report_schedule_update

__verb:__ POST

__params:__

    id - report_schedule.id record to be deleted
    report_type - 
    org_id - organisation UUID
    sub_org_ids - comma separated list of sub-org UUIDs
    frequency - 'monthly' or 'yearly'
    user_roles - comma separated list of org roles, e.g. 'admin,editor'
    emails - comma separated list of email addresses

### report_schedule_delete

__verb:__ GET

__params:__

    id - report_schedule.id record to be deleted

### report_schedule_list


__verb:__ GET

__params:__

    state - 'active' or 'deleted' - default = ALL

### reports_list

__verb:__ GET

__params:__

    id - report_schedule.id record to retrieve records for

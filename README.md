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

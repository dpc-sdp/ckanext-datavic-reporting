# ckanext-datavic-reporting

Custom CKAN reporting extension for Data.Vic

Report organization stats with preconfigured frequency using a combination of report schedule entities and report jobs executed on the schedule

## Requirements

Requires python v3.7 or greater.

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | yes         |
| 2.10         | yes         |


## Installation

To install ckanext-datavic-reporting:

1. Clone the repository
1. Install it via **pip**:
   ```sh
   pip install -e ckanext-datavic-reporting`
   ```
1. Add `datavic_reporting` to the `ckan.plugins` setting in your CKAN config file.
1. Run DB migrations:
   ```sh
   ckan db upgrade -p datavic_reporting
   ```

## Configuration

```ini
# Base path to store reports.
# (default: /tmp)
ckan.datavic_reporting.scheduled_reports_path = /var/log/datavic/reports


# The scheduled reporting frequencies list is configurable comma seperated
# string from the ckan admin config page /ckan-admin/config
# Each frequencies is separated by a comma
ckan.datavic_reporting.scheduled_reporting_frequencies = monthly,yearly
```

## Creating Scheduled Report Job

To create the scheduled report job a CLI command is used.
The command accepts a frequency parameter which used to filter scheduled reports by frequency.
Reports are created for the scheduled report to the file system using the following path and naming conventions:
`{ckan.datavic_reporting.scheduled_reports_path}/org_id/{yyyy}/{mm}/general_report_{timestamp}.csv`

Before running the command configure the CKAN config file:
```ini
ckan.datavic_reporting.scheduled_reports_path = /app/filestore/reports
```

To run the command (Replace `{frequency}` with `monthly` or `yearly`):
```sh
. /app/ckan/default/bin/activate

ckan datavic_reporting createjob {frequency} --config=/app/ckan/default/production.ini
```

## API Endpoints

This extension adds the following endpoints to the CKAN API

### datavic_reporting_schedule_create

    user_id(str, optional): ID of the schedule owner. Defaults to the current user's ID
    report_type(str): At the moment, only `general` type supported
    org_id(str): ID of the organization for reporting
    sub_org_ids(str, optional): comma-separated list of groups for reporting
    user_roles(str): comma-separated list of user-roles for reporting
    emails(str): comma-separated list of emails for reporting
    frequency(str): frequency of reporting

### datavic_reporting_schedule_update

    id(str): ID of the report schedule record
    user_roles(str, optional): comma-separated list of user-roles for reporting
    emails(str, optional): comma-separated list of emails for reporting
    frequency(str, optional): frequency of reporting

### datavic_reporting_schedule_delete

    id(str): report_schedule.id record to be deleted

### datavic_reporting_schedule_list

    frequency(str, optional): frequency of reporting
    state(str, optional): state of the report

### datavic_reporting_job_list

    report_schedule_id(str): ID of related report schedule

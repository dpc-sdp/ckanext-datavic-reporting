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

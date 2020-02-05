import ckan.plugins.toolkit as toolkit
import ckan.model as model
from model import GroupTreeNode
import datetime
import csv
import calendar
from dateutil import parser
import math
import logging

log = logging.getLogger(__name__)


def get_context():
    return {
        'model': model,
        'session': model.Session,
        'user': toolkit.c.user,
    }


def user_report_get_years():
    now = datetime.datetime.now()
    years = []
    current_year = int(now.strftime('%Y'))
    # 2014 is when the first datasets where created so only go back as far as 2014
    for i in range(current_year, 2013, -1):
        year = datetime.date(i, now.month, now.day).strftime('%Y')
        years.append({'value': year, 'text': year})

    return years, current_year


def user_report_get_months():
    now = datetime.datetime.now()
    months = []
    for i in range(1, 13):
        months.append({'value': '{num:02d}'.format(num=i),
                       'text': datetime.date(now.year, i, 1).strftime('%b')})

    return months, now.strftime('%m')


def get_year_month(year, month):
    now = datetime.datetime.now()

    if not year:
        year = now.year

    if not month:
        month = now.month

    return int(year), int(month)


def get_report_date_range(year, month):
    month_range = calendar.monthrange(year, month)

    start_date = datetime.datetime(year, month, 1).strftime('%Y-%m-%d')
    end_date = datetime.datetime(
        year, month, month_range[1]).strftime('%Y-%m-%d')

    return start_date, end_date


def get_top_level_organisation_list_for_user():
    organisations = [{'value': '', 'text': 'All Organisations'}]
    for organisation in model.Group.get_top_level_groups('organization'):
        organisations.append({'value': organisation.name, 'text': organisation.display_name})

    return organisations


def get_organisation(organisation_name):
    return model.Group.get(organisation_name)


def get_organisation_children(organisation_name):
    organisation = get_organisation(organisation_name)
    if not organisation:
        return []
    return organisation.get_children_group_hierarchy('organization')


def get_organisation_children_names(organisation_name):
    if not organisation_name:
        return None
    organisation_names = [organisation_name]
    for group_id, group_name, group_title, parent_id in get_organisation_children(organisation_name):
        organisation_names.append(group_name)

    return organisation_names


def get_organisation_node(organisation_name):
    organisation = get_organisation(organisation_name)
    if not organisation:
        return None
    nodes = {}
    root_node = nodes[organisation.id] = GroupTreeNode({'id': '', 'title': 'All Sub Organisations'})

    for group_id, group_name, group_title, parent_id in organisation.get_children_group_hierarchy('organization'):
        node = GroupTreeNode({'id': group_name, 'title': group_title})
        nodes[parent_id].add_child_node(node)
        nodes[group_id] = node

    return root_node


def get_organisation_node_tree(organisation_name):
    organisation_children = []
    if not organisation_name:
        return organisation_children
    root_node = get_organisation_node(organisation_name)
    if not root_node:
        return organisation_children

    buildOrganisationTree(organisation_children, root_node)
    return organisation_children


def buildOrganisationTree(organisation_tree, organisation, ansestors=0):
    dashes = '-' * ansestors
    text = dashes + str(organisation['title'])
    tree_node = {'value': organisation['id'], 'text': text}
    organisation_tree.append(tree_node)
    if len(organisation['children']) > 0:
        ansestors += 1
        for child_organisation in organisation['children']:
            buildOrganisationTree(organisation_tree, child_organisation, ansestors)
    else:
        ansestors = 0


def value(dataset_dict, field):
    value = dataset_dict.get(field, '')
    return value.encode('ascii', 'ignore') if value else ''


def format_date(date_value):
    return parser.parse(date_value).strftime('%Y-%m-%d') if date_value else ''


def format_bool(dataset_dict, field):
    return 'Yes' if dataset_dict.get(field, False) else 'No'


def get_package_search(data_dict):
    try:
        return toolkit.get_action('package_search')(get_context(), data_dict)
    except Exception as e:
        log.debug(
            '*** Failed to retrieve package_search query {0}'.format(data_dict))
        log.debug(e)
        return None


def get_dataset_data(start_date, end_date, start_offset, organisation_names):
    date_query = ''
    if start_date and end_date:
        date_query = '(metadata_created:[{0}T00:00:00.000Z TO {1}T23:59:59.999Z] OR metadata_modified:[{0}T00:00:00.000Z TO {1}T23:59:59.999Z]) AND '.format(start_date, end_date)
    elif end_date:
        date_query = '(metadata_created:[* TO {0}T23:59:59.999Z] OR metadata_modified:[* TO {0}T23:59:59.999Z]) AND '.format(end_date)
    elif start_date:
        date_query = '(metadata_created:[{0}T00:00:00.000Z TO *] OR metadata_modified:[{0}T00:00:00.000Z TO *]) AND '.format(start_date)

    workflow_query = '(workflow_status:published OR workflow_status:archived)'
    organisation_query = ' AND (organization:{0})'.format(' OR organization:'.join(map(str, organisation_names))) if organisation_names else ''
    data_dict = {
        'q': '{0} {1} {2}'.format(date_query, workflow_query, organisation_query),
        'sort': 'metadata_created asc, metadata_modified asc',
        'include_private': True,
        'start': start_offset,
        'rows': 1000
    }
    return get_package_search(data_dict)


def get_general_report_data(csv_writer, start_date, end_date, start_offset, organisation_names):
    total_results_found = 0

    dataset_data = get_dataset_data(start_date, end_date, start_offset, organisation_names)
    if dataset_data:
        total_results_found = dataset_data['count']
        write_csv_row(csv_writer, dataset_data['results'])

    return total_results_found


def write_csv_row(csv_writer, dataset_list):
    if dataset_list:
        for dataset_dict in dataset_list:
            row = []
            row.append(value(dataset_dict, 'title'))
            row.append(value(dataset_dict, 'extract'))
            row.append(value(dataset_dict, 'notes'))
            row.append(value(dataset_dict['organization'], 'title')
                       if 'organization' in dataset_dict and dataset_dict['organization'] != None else '')
            row.append(', '.join([value(group, 'title')
                                  for group in dataset_dict['groups']])
                       if 'groups' in dataset_dict and dataset_dict['groups'] != None else '')
            row.append(value(dataset_dict, 'agency_program'))
            row.append('No' if dataset_dict.get('private', False) else 'Yes')
            row.append(value(dataset_dict, 'workflow_status'))
            row.append(format_date(value(dataset_dict, 'metadata_modified')))
            row.append(format_date(value(dataset_dict, 'metadata_created')))

            csv_writer.writerow(row)

            for resource in dataset_dict['resources']:
                res_list = []
                res_list.append(
                    value(resource, 'url') if 'url' in resource and resource['url'] != None else '')
                res_list.append(
                    value(resource, 'format') if 'format' in resource and resource['format'] != None else '')
                res_list.append(
                    value(resource, 'release_date') if 'release_date' in resource and resource['release_date'] != None else '')
                res_list.append(
                    value(resource, 'period_start') if 'period_start' in resource and resource['period_start'] != None else '')
                res_list.append(
                    value(resource, 'period_end') if 'period_end' in resource and resource['period_end'] != None else '')

                csv_writer.writerow(row + res_list)


def generate_general_report(filename, start_date, end_date, organisation):
    csv_writer = csv.writer(open('/tmp/' + filename, 'wb'))

    header = [
        'Title',
        'Extract',
        'Description',
        'Organisation',
        'Groups',
        'Agency Program',
        'Public Release',
        'Workflow Status',
        'Last modified',
        'Created date',
        'Resource URL',
        'Resource Format',
        'Resource Release Date',
        'Resource Period Start',
        'Resource Period End'
    ]

    csv_writer.writerow(header)
    start_date = format_date(start_date)
    end_date = format_date(end_date)
    organisation_names = get_organisation_children_names(organisation)
    total_results_found = get_general_report_data(csv_writer, start_date, end_date, 0, organisation_names)
    # package_search is hard coded to only return the first 1000 datasets and cannot be changed to return anymore
    # So if there is a large date range which returns over a 1000 datasets we will need to loop through to get the remaining datasets
    if total_results_found > 1000:
        start = 1000
        step = 1000
        # Calculate the reminder of the datasets and round it up to the nearest 1000
        stop = int(math.ceil(total_results_found / 1000.0) * step)

        for start_offset in range(start, stop, step):
            get_general_report_data(csv_writer, start_date, end_date, start_offset, organisation_names)

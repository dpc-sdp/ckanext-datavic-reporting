import csv
import datetime
import logging
import math
import mimetypes
import os

import ckan.model as model
import ckan.plugins.toolkit as toolkit
import pytz
from ckan.lib.navl.dictization_functions import unflatten
from ckan.logic import clean_dict, parse_params, tuplize_dict
from ckan.views.user import _extra_template_variables
from dateutil import parser
from flask import send_from_directory

from ckanext.datavic_reporting.model import GroupTreeNode
from ckanext.toolbelt.decorators import Collector
from .logic import auth


helper, get_helpers = Collector("datavic_reporting").split()

config = toolkit.config
log = logging.getLogger(__name__)


def get_context():
    return {
        "model": model,
        "session": model.Session,
        "user": toolkit.g.user,
        "auth_user_obj": get_user(),
    }


def get_user():
    return toolkit.g.userobj


def get_username():
    try:
        return toolkit.g.user
    except AttributeError:
        pass


@helper
def get_years():
    now = datetime.datetime.now()
    years = []
    current_year = int(now.strftime("%Y"))
    # 2014 is when the first datasets where created so only go back as far as 2014
    for i in range(current_year, 2013, -1):
        year = datetime.date(i, now.month, now.day).strftime("%Y")
        years.append({"value": year, "text": year})

    return years, current_year


@helper
def get_months():
    now = datetime.datetime.now()
    months = []
    for i in range(1, 13):
        months.append(
            {
                "value": "{num:02d}".format(num=i),
                "text": datetime.date(now.year, i, 1).strftime("%b"),
            }
        )

    return months, now.strftime("%m")


@helper
def organisations():
    orgs = []
    top_level_organisations = _get_top_level_orgs()
    if not toolkit.request or toolkit.h.check_access("sysadmin"):
        orgs = top_level_organisations
    elif auth.has_user_permission_for_some_org(get_username(), "admin"):
        for user_organisation in _orgs_for_user("admin"):
            orgs.append(
                {
                    "value": user_organisation.get("name"),
                    "text": user_organisation.get("display_name"),
                }
            )

    orgs.insert(0, {"value": "all-organisations", "text": "All Organisations"})
    return orgs


def _get_top_level_orgs():
    orgs = []
    for organisation in model.Group.get_top_level_groups("organization"):
        orgs.append(
            {"value": organisation.name, "text": organisation.display_name}
        )

    return orgs


def _orgs_for_user(permission):
    try:
        return toolkit.get_action("organization_list_for_user")(
            get_context(), {"permission": permission}
        )
    except Exception as e:
        log.error(
            "*** Failed to retrieve organization_list_for_user {0}".format(
                get_username()
            )
        )
        log.error(e)
        return []


def get_organisation(organisation_name):
    return model.Group.get(organisation_name)


def _organisation_children(organisation_name):
    organisation = get_organisation(organisation_name)
    if not organisation:
        return []
    return organisation.get_children_group_hierarchy("organization")


def get_organisation_children_names(organisation_name):
    organisation_names = []

    if not toolkit.request or toolkit.h.check_access("sysadmin"):
        if organisation_name != "all-organisations":
            organisation_names.append(organisation_name)
            for (
                group_id,
                group_name,
                group_title,
                parent_id,
            ) in _organisation_children(organisation_name):
                organisation_names.append(group_name)
    elif auth.has_user_permission_for_some_org(get_username(), "admin"):
        user_organisations = _orgs_for_user("admin")
        if organisation_name == "all-organisations":
            for user_organisation in user_organisations:
                organisation_names.append(user_organisation.get("name"))
        else:
            organisation_names.append(organisation_name)
            for (
                group_id,
                group_name,
                group_title,
                parent_id,
            ) in _organisation_children(organisation_name):
                for user_organisation in user_organisations:
                    if user_organisation.get("name") == group_name:
                        organisation_names.append(group_name)

    return organisation_names


def _org_node(organisation_name):
    organisation = get_organisation(organisation_name)
    if not organisation:
        return None
    nodes = {}
    root_node = nodes[organisation.id] = GroupTreeNode(
        {"id": "all-sub-organisations", "title": "All Sub Organisations"}
    )

    for (
        group_id,
        group_name,
        group_title,
        parent_id,
    ) in organisation.get_children_group_hierarchy("organization"):
        node = GroupTreeNode({"id": group_name, "title": group_title})
        nodes[parent_id].add_child_node(node)
        nodes[group_id] = node

    return root_node


@helper
def organisation_tree(organisation_name):
    organisation_children = []
    if not organisation_name:
        return organisation_children
    root_node = _org_node(organisation_name)
    if not root_node:
        return organisation_children

    user_organisations = _orgs_for_user("admin")
    _build_org_tree(user_organisations, organisation_children, root_node)
    return organisation_children


def _has_access_to_organisation(user_organisations, organisation_name):
    for user_organisation in user_organisations:
        if (
            user_organisation.get("name") == organisation_name
            or organisation_name == "all-sub-organisations"
        ):
            return True

    return False


def _build_org_tree(
    user_organisations, organisation_tree, organisation, ansestors=0
):
    dashes = "-" * ansestors
    text = dashes + str(organisation["title"])
    has_access = _has_access_to_organisation(
        user_organisations, organisation["id"]
    )
    tree_node = {
        "value": organisation["id"],
        "text": text,
        "has_access": has_access,
    }
    organisation_tree.append(tree_node)
    if len(organisation["children"]) > 0:
        ansestors += 1
        for child_organisation in organisation["children"]:
            _build_org_tree(
                user_organisations,
                organisation_tree,
                child_organisation,
                ansestors,
            )
    else:
        ansestors = 0


def _value(dataset_dict, field):
    value = dataset_dict.get(field, "")
    return value.encode("ascii", "ignore").decode("ascii") if value else ""


def _markdown_extract(value: str) -> str:
    return toolkit.h.markdown_extract(value)


def format_date(date_value):
    return parser.parse(date_value).strftime("%Y-%m-%d") if date_value else ""


def _package_search(data_dict):
    try:
        return toolkit.get_action("package_search")(get_context(), data_dict)
    except Exception as e:
        log.error(
            "*** Failed to retrieve package_search query {0}".format(data_dict)
        )
        log.error(e)
        return None


def _dataset_data(start_date, end_date, start_offset, organisation_names):
    query = []
    if start_date and end_date:
        query.append(
            "(metadata_created:[{0}T00:00:00.000Z TO {1}T23:59:59.999Z] OR"
            " metadata_modified:[{0}T00:00:00.000Z TO {1}T23:59:59.999Z])"
            .format(start_date, end_date)
        )
    elif end_date:
        query.append(
            "(metadata_created:[* TO {0}T23:59:59.999Z] OR"
            " metadata_modified:[* TO {0}T23:59:59.999Z])".format(end_date)
        )
    elif start_date:
        query.append(
            "(metadata_created:[{0}T00:00:00.000Z TO *] OR"
            " metadata_modified:[{0}T00:00:00.000Z TO *])".format(start_date)
        )

    if organisation_names:
        query.append(
            "(organization:{0})".format(
                " OR organization:".join(map(str, organisation_names))
            )
        )

    data_dict = {
        "q": " AND ".join(query),
        "sort": "metadata_created asc, metadata_modified asc",
        "include_private": True,
        "start": start_offset,
        "rows": 1000,
    }
    log.debug("Package Search Query: {0}".format(data_dict))
    return _package_search(data_dict)


def _general_report_data(
    csv_writer, start_date, end_date, start_offset, organisation_names
):
    total_results_found = 0

    dataset_data = _dataset_data(
        start_date, end_date, start_offset, organisation_names
    )
    if dataset_data:
        total_results_found = dataset_data["count"]
        _write_csv_row(csv_writer, dataset_data["results"])

    return total_results_found


def _write_csv_row(csv_writer, dataset_list):
    if dataset_list:
        for dataset_dict in dataset_list:
            row = []
            row.append(_value(dataset_dict, "title"))
            row.append(_value(dataset_dict, "extract"))
            row.append(_markdown_extract(_value(dataset_dict, "notes")))
            row.append(
                _value(dataset_dict["organization"], "title")
                if "organization" in dataset_dict
                and dataset_dict["organization"] != None
                else ""
            )
            row.append(
                ", ".join(
                    [
                        _value(group, "title")
                        for group in dataset_dict["groups"]
                    ]
                )
                if "groups" in dataset_dict and dataset_dict["groups"] != None
                else ""
            )
            row.append(_value(dataset_dict, "agency_program"))
            row.append("No" if dataset_dict.get("private", False) else "Yes")
            row.append(_value(dataset_dict, "workflow_status"))
            row.append(format_date(_value(dataset_dict, "metadata_modified")))
            row.append(format_date(_value(dataset_dict, "metadata_created")))

            csv_writer.writerow(row)

            for resource in dataset_dict["resources"]:
                res_list = []
                res_list.append(
                    _value(resource, "url")
                    if "url" in resource and resource["url"] != None
                    else ""
                )
                res_list.append(
                    _value(resource, "format")
                    if "format" in resource and resource["format"] != None
                    else ""
                )
                res_list.append(
                    _value(resource, "release_date")
                    if "release_date" in resource
                    and resource["release_date"] != None
                    else ""
                )
                res_list.append(
                    _value(resource, "period_start")
                    if "period_start" in resource
                    and resource["period_start"] != None
                    else ""
                )
                res_list.append(
                    _value(resource, "period_end")
                    if "period_end" in resource
                    and resource["period_end"] != None
                    else ""
                )

                csv_writer.writerow(row + res_list)


def generate_general_report(
    path, filename, start_date, end_date, organisation
):
    # Create directory structure if it does not exist
    try:
        os.makedirs(path)
    except OSError as e:
        if not os.path.isdir(path):
            log.error(e)
            raise
    csv_writer = csv.writer(open(path + filename, "w"))

    header = [
        "Title",
        "Extract",
        "Description",
        "Organisation",
        "Groups",
        "Agency Program",
        "Public Release",
        "Workflow Status",
        "Last modified",
        "Created date",
        "Resource URL",
        "Resource Format",
        "Resource Release Date",
        "Resource Period Start",
        "Resource Period End",
    ]

    csv_writer.writerow(header)
    start_date = format_date(start_date)
    end_date = format_date(end_date)
    organisation_names = get_organisation_children_names(organisation)
    total_results_found = _general_report_data(
        csv_writer, start_date, end_date, 0, organisation_names
    )
    # package_search is hard coded to only return the first 1000 datasets and cannot be changed to return anymore
    # So if there is a large date range which returns over a 1000 datasets we will need to loop through to get the remaining datasets
    if total_results_found > 1000:
        start = 1000
        step = 1000
        # Calculate the reminder of the datasets and round it up to the nearest 1000
        stop = int(math.ceil(total_results_found / 1000.0) * step)

        for start_offset in range(start, stop, step):
            _general_report_data(
                csv_writer,
                start_date,
                end_date,
                start_offset,
                organisation_names,
            )


def clean_params(params):
    return clean_dict(unflatten(tuplize_dict(parse_params(params))))


@helper
def report_schedules(state=None):
    result = toolkit.get_action("datavic_reporting_schedule_list")(
        {}, {"state": state}
    )
    return result


@helper
def schedule_organizations():
    orgs = []
    top_level_organisations = _get_top_level_orgs()
    if not toolkit.request or toolkit.h.check_access("sysadmin"):
        orgs = top_level_organisations

    orgs.insert(0, {"value": "", "text": "Please select"})
    return orgs


def get_organisation_role_emails(context, id, role):
    user_emails = []
    data_dict = {
        "id": id,
        "include_dataset_count": False,
        "include_extras": False,
        "include_users": True,
        "include_groups": False,
        "include_tags": False,
        "include_followers": False,
    }
    organisation = toolkit.get_action("organization_show")(
        context, data_dict=data_dict
    )
    for org_user in organisation.get("users"):
        if org_user.get("capacity") == role:
            user = toolkit.get_action("user_show")(
                context, data_dict={"id": org_user.get("id")}
            )
            user_email = user.get("email")
            if user_email:
                user_emails.append(user_email)
    return user_emails if user_emails else None


def download_file(directory, filename):
    return send_from_directory(
        directory,
        filename,
        mimetype="text/csv",
        as_attachment=True,
        attachment_filename=filename,
    )


def get_scheduled_report_frequencies():
    frequencies = toolkit.config.get(
        "ckan.datavic_reporting.scheduled_reporting_frequencies", []
    ).split(",")
    return [frequency.lower() for frequency in frequencies]


@helper
def schedule_frequencies():
    frequencies = []
    for frequency in get_scheduled_report_frequencies():
        frequencies.append(
            {"value": frequency, "text": frequency.capitalize()}
        )

    return frequencies


@helper
def member_state(member):
    state = member.state
    if state == "pending":
        state += (
            " (Review required)"
            if not member.reset_key
            else " (Invite not active)"
        )
    return state


def generate_member_report(path, filename, data_dict):
    # Create directory structure if it does not exist
    try:
        os.makedirs(path)
    except OSError as e:
        if not os.path.isdir(path):
            log.error(e)
            raise
    csv_writer = csv.writer(open(path + filename, "w"))

    header_row = [
        "Organisation",
        "Username",
        "Email",
        "Capacity",
        "State",
        "Created",
    ]

    csv_writer.writerow(header_row)

    members = toolkit.get_action("datavic_reporting_organisation_members")(
        get_context(), data_dict
    )

    ckan_timezone = config.get("ckan.display_timezone", None)
    tz = pytz.timezone("UTC")

    for member in members:
        row = [
            member.organisation_name.encode("ascii", "ignore").decode("ascii"),
            member.username.encode("ascii", "ignore").decode("ascii"),
            member.email.encode("ascii", "ignore").decode("ascii"),
            member.capacity.encode("ascii", "ignore").decode("ascii"),
            member_state(member).encode("ascii", "ignore").decode("ascii"),
            tz.localize(member.created).astimezone(
                pytz.timezone(ckan_timezone)
            ),
        ]

        csv_writer.writerow(row)


@helper
def user_states():
    return [
        {"text": "All states", "value": ""},
        {"text": "Active", "value": "active"},
        {"text": "Pending (Invite not active)", "value": "pending_invited"},
        {"text": "Pending (Review required)", "value": "pending_request"},
    ]


def setup_extra_template_variables():
    user = get_user()
    context = {"for_view": True, "user": get_username(), "auth_user_obj": user}
    data_dict = {"user_obj": user, "include_datasets": True}
    return _extra_template_variables(context, data_dict)

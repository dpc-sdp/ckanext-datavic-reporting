import ckanext.datavic_reporting.authorisation as authorisation
import calendar
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import csv
import datetime
import logging
import math
import mimetypes
import os
import pytz
import sqlalchemy
import pkgutil
import inspect

from ckan.lib.navl.dictization_functions import unflatten
from ckan.logic import clean_dict, tuplize_dict, parse_params
from dateutil import parser
from ckanext.datavic_reporting.model import GroupTreeNode
from flask import send_from_directory, Blueprint
from ckan.views.user import _extra_template_variables

_and_ = sqlalchemy.and_
_session_ = model.Session
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
    return get_user().name


def user_report_get_years():
    now = datetime.datetime.now()
    years = []
    current_year = int(now.strftime("%Y"))
    # 2014 is when the first datasets where created so only go back as far as 2014
    for i in range(current_year, 2013, -1):
        year = datetime.date(i, now.month, now.day).strftime("%Y")
        years.append({"value": year, "text": year})

    return years, current_year


def user_report_get_months():
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


def get_year_month(year, month):
    now = datetime.datetime.now()

    if not year:
        year = now.year

    if not month:
        month = now.month

    return int(year), int(month)


def get_report_date_range(year, month):
    month_range = calendar.monthrange(year, month)

    start_date = datetime.datetime(year, month, 1).strftime("%Y-%m-%d")
    end_date = datetime.datetime(year, month, month_range[1]).strftime(
        "%Y-%m-%d"
    )

    return start_date, end_date


def get_organisation_list():
    organisations = []
    top_level_organisations = get_top_level_organisation_list()
    if authorisation.is_sysadmin():
        organisations = top_level_organisations
    elif authorisation.has_user_permission_for_some_org(
        get_username(), "admin"
    ):
        for user_organisation in get_organisation_list_for_user("admin"):
            organisations.append(
                {
                    "value": user_organisation.get("name"),
                    "text": user_organisation.get("display_name"),
                }
            )

    organisations.insert(
        0, {"value": "all-organisations", "text": "All Organisations"}
    )
    return organisations


def get_top_level_organisation_list():
    organisations = []
    for organisation in model.Group.get_top_level_groups("organization"):
        organisations.append(
            {"value": organisation.name, "text": organisation.display_name}
        )

    return organisations


def get_organisation_list_for_user(permission):
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


def get_organisation_children(organisation_name):
    organisation = get_organisation(organisation_name)
    if not organisation:
        return []
    return organisation.get_children_group_hierarchy("organization")


def get_organisation_children_names(organisation_name):
    organisation_names = []

    if authorisation.is_sysadmin():
        if organisation_name != "all-organisations":
            organisation_names.append(organisation_name)
            for (
                group_id,
                group_name,
                group_title,
                parent_id,
            ) in get_organisation_children(organisation_name):
                organisation_names.append(group_name)
    elif authorisation.has_user_permission_for_some_org(
        get_username(), "admin"
    ):
        user_organisations = get_organisation_list_for_user("admin")
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
            ) in get_organisation_children(organisation_name):
                for user_organisation in user_organisations:
                    if user_organisation.get("name") == group_name:
                        organisation_names.append(group_name)

    return organisation_names


def get_organisation_node(organisation_name):
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


def get_organisation_node_tree(organisation_name):
    organisation_children = []
    if not organisation_name:
        return organisation_children
    root_node = get_organisation_node(organisation_name)
    if not root_node:
        return organisation_children

    user_organisations = get_organisation_list_for_user("admin")
    buildOrganisationTree(user_organisations, organisation_children, root_node)
    return organisation_children


def has_access_to_organisation(user_organisations, organisation_name):
    for user_organisation in user_organisations:
        if (
            user_organisation.get("name") == organisation_name
            or organisation_name == "all-sub-organisations"
        ):
            return True

    return False


def buildOrganisationTree(
    user_organisations, organisation_tree, organisation, ansestors=0
):
    dashes = "-" * ansestors
    text = dashes + str(organisation["title"])
    has_access = has_access_to_organisation(
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
            buildOrganisationTree(
                user_organisations,
                organisation_tree,
                child_organisation,
                ansestors,
            )
    else:
        ansestors = 0


def value(dataset_dict, field):
    value = dataset_dict.get(field, "")
    return value.encode("ascii", "ignore").decode("ascii") if value else ""


def format_date(date_value):
    return parser.parse(date_value).strftime("%Y-%m-%d") if date_value else ""


def format_bool(dataset_dict, field):
    return "Yes" if dataset_dict.get(field, False) else "No"


def get_package_search(data_dict):
    try:
        return toolkit.get_action("package_search")(get_context(), data_dict)
    except Exception as e:
        log.error(
            "*** Failed to retrieve package_search query {0}".format(data_dict)
        )
        log.error(e)
        return None


def get_dataset_data(start_date, end_date, start_offset, organisation_names):
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
    return get_package_search(data_dict)


def get_general_report_data(
    csv_writer, start_date, end_date, start_offset, organisation_names
):
    total_results_found = 0

    dataset_data = get_dataset_data(
        start_date, end_date, start_offset, organisation_names
    )
    if dataset_data:
        total_results_found = dataset_data["count"]
        write_csv_row(csv_writer, dataset_data["results"])

    return total_results_found


def write_csv_row(csv_writer, dataset_list):
    if dataset_list:
        for dataset_dict in dataset_list:
            row = []
            row.append(value(dataset_dict, "title"))
            row.append(value(dataset_dict, "extract"))
            row.append(value(dataset_dict, "notes"))
            row.append(
                value(dataset_dict["organization"], "title")
                if "organization" in dataset_dict
                and dataset_dict["organization"] != None
                else ""
            )
            row.append(
                ", ".join(
                    [value(group, "title") for group in dataset_dict["groups"]]
                )
                if "groups" in dataset_dict and dataset_dict["groups"] != None
                else ""
            )
            row.append(value(dataset_dict, "agency_program"))
            row.append("No" if dataset_dict.get("private", False) else "Yes")
            row.append(value(dataset_dict, "workflow_status"))
            row.append(format_date(value(dataset_dict, "metadata_modified")))
            row.append(format_date(value(dataset_dict, "metadata_created")))

            csv_writer.writerow(row)

            for resource in dataset_dict["resources"]:
                res_list = []
                res_list.append(
                    value(resource, "url")
                    if "url" in resource and resource["url"] != None
                    else ""
                )
                res_list.append(
                    value(resource, "format")
                    if "format" in resource and resource["format"] != None
                    else ""
                )
                res_list.append(
                    value(resource, "release_date")
                    if "release_date" in resource
                    and resource["release_date"] != None
                    else ""
                )
                res_list.append(
                    value(resource, "period_start")
                    if "period_start" in resource
                    and resource["period_start"] != None
                    else ""
                )
                res_list.append(
                    value(resource, "period_end")
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
    total_results_found = get_general_report_data(
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
            get_general_report_data(
                csv_writer,
                start_date,
                end_date,
                start_offset,
                organisation_names,
            )


def clean_params(params):
    return clean_dict(unflatten(tuplize_dict(parse_params(params))))


def get_report_schedules(state=None):
    result = toolkit.get_action("report_schedule_list")({}, {"state": state})
    return result.get("result") if result.get("success", False) == True else []


def get_report_schedule_organisation_list():
    organisations = []
    top_level_organisations = get_top_level_organisation_list()
    if authorisation.is_sysadmin():
        organisations = top_level_organisations

    organisations.insert(0, {"value": "", "text": "Please select"})
    return organisations


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


def get_file_type(filename):
    ctype, encoding = mimetypes.guess_type(filename)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    return ctype


def get_scheduled_report_frequencies():
    frequencies = toolkit.config.get(
        "ckan.datavic_reporting.scheduled_reporting_frequencies", []
    ).split(",")
    return [frequency.lower() for frequency in frequencies]


def get_scheduled_report_frequencies_list():
    frequencies = []
    for frequency in get_scheduled_report_frequencies():
        frequencies.append(
            {"value": frequency, "text": frequency.capitalize()}
        )

    return frequencies


def display_member_state(member):
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

    members = toolkit.get_action("organisation_members")(
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
            display_member_state(member)
            .encode("ascii", "ignore")
            .decode("ascii"),
            tz.localize(member.created).astimezone(
                pytz.timezone(ckan_timezone)
            ),
        ]

        csv_writer.writerow(row)


def get_user_states():
    return [
        {"text": "All states", "value": ""},
        {"text": "Active", "value": "active"},
        {"text": "Pending (Invite not active)", "value": "pending_invited"},
        {"text": "Pending (Review required)", "value": "pending_request"},
    ]


def _register_blueprints():
    """Return all blueprints defined in the `views` folder"""
    blueprints = []

    def is_blueprint(mm):
        return isinstance(mm, Blueprint)

    path = os.path.join(os.path.dirname(__file__), "views")

    for loader, name, _ in pkgutil.iter_modules([path]):
        module = loader.find_module(name).load_module(name)
        for blueprint in inspect.getmembers(module, is_blueprint):
            blueprints.append(blueprint[1])
            log.info("Registered blueprint: {0!r}".format(blueprint[0]))
    return blueprints


def setup_extra_template_variables():
    user = get_user()
    context = {"for_view": True, "user": get_username(), "auth_user_obj": user}
    data_dict = {"user_obj": user, "include_datasets": True}
    return _extra_template_variables(context, data_dict)

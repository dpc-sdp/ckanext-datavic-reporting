from __future__ import annotations

import datetime
import logging

import ckan.authz as authz
import ckan.model as model
import ckan.plugins.toolkit as tk
import sqlalchemy
from ckan.logic import validate
from ckan.model.group import Group, Member
from ckan.model.user import User
from sqlalchemy.orm import aliased

import ckanext.datavic_reporting.constants as constants
import ckanext.datavic_reporting.helpers as helpers
import ckanext.datavic_reporting.mailer as mailer
from ckanext.datavic_reporting.model import ReportJob, ReportSchedule
from ckanext.toolbelt.decorators import Collector

from . import schema

_and_ = sqlalchemy.and_
_session_ = model.Session
log = logging.getLogger(__name__)

CONFIG_REPORT_PATH = "ckan.datavic_reporting.scheduled_reports_path"

DEFAULT_REPORT_PATH = "/tmp"


action, get_actions = Collector("datavic_reporting").split()


@action
@validate(schema.schedule_create)
def schedule_create(context, data_dict):
    """Create new report schedule

    Args:
        user_id(str, optional): ID of the schedule owner. Defaults to the current user's ID
        report_type(str): At the moment, only `general` type supported
        org_id(str): ID of the organization for reporting
        sub_org_ids(str, optional): comma-separated list of groups for reporting
        user_roles(str): comma-separated list of user-roles for reporting
        emails(str): comma-separated list of emails for reporting
        frequency(str): frequency of reporting
    """
    sess = context["session"]
    tk.check_access("datavic_reporting_schedule_create", context, {})

    if "user_id" not in data_dict:
        user = context["model"].User.get(context["user"])
        data_dict["user_id"] = user.id

    schedule = ReportSchedule(state="active", **data_dict)
    sess.add(schedule)
    sess.commit()
    return schedule.as_dict()


@action
@validate(schema.schedule_update)
def schedule_update(context, data_dict):
    """Create update report schedule

    Args:
        id(str): ID of the report schedule record
        user_roles(str, optional): comma-separated list of user-roles for reporting
        emails(str, optional): comma-separated list of emails for reporting
        frequency(str, optional): frequency of reporting
    """
    tk.check_access("datavic_reporting_schedule_update", context, {})

    schedule = ReportSchedule.get(data_dict["id"])
    if not schedule:
        raise tk.ObjectNotFound()

    for k, v in data_dict.items():
        setattr(schedule, k, v)
    context["session"].commit()

    return schedule.as_dict()


@action
@tk.side_effect_free
@validate(schema.schedule_list)
def schedule_list(context, data_dict):
    """List report schedules

    Args:
        frequency(str, optional): frequency of reporting
        state(str, optional): state of the report

    """
    tk.check_access("datavic_reporting_schedule_list", context, {})

    state = data_dict.get("state", None)
    frequency = data_dict.get("frequency", None)

    q = model.Session.query(ReportSchedule)

    if state:
        q = q.filter_by(state=state)

    if frequency:
        q = q.filter_by(frequency=frequency)

    return [s.as_dict() for s in q]


@action
@tk.side_effect_free
@validate(schema.schedule_delete)
def schedule_delete(context, data_dict):
    tk.check_access("datavic_reporting_schedule_delete", context, data_dict)

    schedule = ReportSchedule.get(data_dict["id"])
    if not schedule:
        raise tk.ObjectNotFound()

    reports = tk.get_action("datavic_reporting_job_list")(
        context, {"report_schedule_id": schedule.id}
    )

    if reports:
        schedule.state = "deleted"
    else:
        model.Session.delete(schedule)
    model.Session.commit()

    return schedule.as_dict()


@action
@tk.side_effect_free
@validate(schema.job_list)
def job_list(context, data_dict):
    """List report jobs

    Args:
        report_schedule_id(str): ID of related report schedule
    """
    tk.check_access("datavic_reporting_job_list", context, {})
    report_jobs = (
        context["session"]
        .query(ReportJob)
        .filter_by(report_schedule_id=data_dict["report_schedule_id"])
    )
    return [r.as_dict() for r in report_jobs]


@action
@validate(schema.job_create)
def job_create(context, data_dict):
    """Create a new report job

    Args:
        id(str): ID of related report schedule
        org_id(str): ID of the organization for reporting
        sub_org_ids(str, optional): comma-separated list of groups for reporting
        user_roles(str): comma-separated list of user-roles for reporting
        emails(str): comma-separated list of emails for reporting
        frequency(str): frequency of reporting

    """
    report_job_path = tk.config.get(CONFIG_REPORT_PATH, DEFAULT_REPORT_PATH)
    sub_org_ids = data_dict.get("sub_org_ids")
    organisation = (
        data_dict.get("org_id")
        if not sub_org_ids or sub_org_ids == "all-sub-organisations"
        else sub_org_ids
    )

    now = datetime.datetime.now()
    path_date = now.strftime("%Y/%m")
    path = f"{report_job_path}/{organisation}/{path_date}/"

    filename = f"general_report_{now.isoformat()}.csv"
    file_path = path + filename

    report_job_dict = {
        "report_schedule_id": data_dict["id"],
        "filename": file_path,
        "frequency": data_dict["frequency"],
        "user_roles": data_dict["user_roles"],
        "emails": data_dict["emails"],
        "status": constants.Statuses.Processing,
    }

    report_job = ReportJob(**report_job_dict)
    model.Session.add(report_job)
    model.Session.commit()

    helpers.generate_general_report(path, filename, None, None, organisation)
    report_job.status = constants.Statuses.Generated
    model.Session.commit()

    user_emails = []
    for user_role in data_dict["user_roles"].split(","):
        role_emails = helpers.get_organisation_role_emails(
            context, organisation, user_role
        )
        if role_emails:
            user_emails.extend(role_emails)

    user_emails.extend(data_dict["emails"].split(","))

    if user_emails:
        extra_vars = {
            "site_title": tk.config.get("ckan.site_title"),
            "site_url": tk.config.get("ckan.site_url"),
            "org_id": organisation,
            "frequency": data_dict["frequency"],
            "date": now.strftime("%Y") + " " + now.strftime("%B"),
            "file_path": file_path,
        }
        mailer.send_scheduled_report_email(
            user_emails, "scheduled_report", extra_vars
        )
        report_job.status = constants.Statuses.EmailsSent
    else:
        report_job.status = constants.Statuses.NoEmails

    model.Session.commit()
    return report_job.as_dict()


@action
@validate(schema.organisation_members)
def organisation_members(context, data_dict):
    """List members of the given organizations

    Args:
        organisations(list[str], optional): names of organizations
        state(str, optional): state of users
    """

    base_query = _session_.query(
        Group.name.label("organisation_name"),
        User.name.label("username"),
        User.email,
        User.state,
        User.created,
        User.reset_key,
        Member.capacity,
    )

    conditions = [
        Group.type == "organization",
        Member.table_name == "user",
        Member.state == "active",
    ]

    organisations = data_dict["organisations"]
    state = data_dict.get("state", None)

    if len(organisations) > 0:
        conditions.append(Group.name.in_(organisations))

    if state == "active":
        conditions.append(User.state == "active")
    elif state == "pending_invited":
        conditions.append(User.state == "pending")
        conditions.append(User.reset_key != None)
    elif state == "pending_request":
        conditions.append(User.state == "pending")
        conditions.append(User.reset_key == None)

    if authz.is_sysadmin(context["user"]):
        # Show all members for sysadmin users
        members = (
            base_query.filter(_and_(*conditions))
            .join(Member, Member.group_id == Group.id)
            .join(User, User.id == Member.table_id)
            .order_by(Group.name.asc(), User.name.asc())
        )

        # log.debug(str(members))

        return members.all()

    tk.check_access("user_dashboard_reports", context, {})

    # For authenticated users who are an admin of at least one organisation
    # only show members of organisations they are an admin of
    user = helpers.get_user()

    authenticated_member = aliased(Member, name="authenticated_member")
    authenticated_user = aliased(User, name="authenticated_user")

    # Only include organisations if authenticated user is an admin
    conditions.append(authenticated_member.table_name == "user")
    conditions.append(authenticated_member.capacity == "admin")
    conditions.append(authenticated_member.table_id == user.id)
    conditions.append(authenticated_member.state == "active")

    return (
        base_query.filter(_and_(*conditions))
        .join(Member, Member.group_id == Group.id)
        .join(User, User.id == Member.table_id)
        # Only include organisations if authenticated user is an admin
        .join(
            authenticated_member,
            authenticated_member.group_id == Group.id,
        )
        .join(
            authenticated_user,
            authenticated_user.id == authenticated_member.table_id,
        )
        .order_by(Group.name.asc(), User.name.asc())
    ).all()

from __future__ import annotations

import datetime
import logging

import ckan.model as model
import sqlalchemy
from ckan.logic import NotAuthorized, side_effect_free, validate
from ckan.model.group import Group, Member
from ckan.model.user import User
from ckan.plugins import toolkit
from sqlalchemy.orm import aliased

import ckanext.datavic_reporting.constants as constants
import ckanext.datavic_reporting.helpers as helpers
import ckanext.datavic_reporting.mailer as mailer
from ckanext.datavic_reporting import authorisation
from ckanext.datavic_reporting.model import ReportJob, ReportSchedule
from ckanext.toolbelt.decorators import Collector

from . import schema

_and_ = sqlalchemy.and_
_session_ = model.Session
log = logging.getLogger(__name__)


action, get_actions = Collector("datavic_reporting").split()


@action("report_schedule_update")
def report_schedule_update(context, data_dict):
    errors = {}

    id = data_dict.get("id", None)

    # Check to make sure `id` looks like a UUID
    if id and model.is_id(id):
        try:
            # Check access - see authorisaton.py for implementation
            toolkit.check_access("report_schedule_update", context, {})

            # Load the record
            schedule = ReportSchedule.get(id)
            if schedule:
                # The list of fields that can be updated is controlled here
                for field in ["frequency", "user_roles", "emails"]:
                    value = data_dict.get(field, None)
                    if value:
                        setattr(schedule, field, value)

                # Validate data_dict inputs - see validators.py for implementations
                validated_data_dict = toolkit.get_validator(
                    "report_schedule_validator"
                )(data_dict, context, "update")

                if validated_data_dict is data_dict:
                    model.Session.add(schedule)
                    model.Session.commit()
                    return True
                else:
                    errors = validated_data_dict
        except Exception as e:
            errors["exception"] = str(e)
    else:
        errors = "Invalid or no report schedule ID provided."

    return {"errors": errors}


@action("report_schedule_list")
@side_effect_free
def report_schedule_list(context, data_dict):
    state = data_dict.get("state", None)
    frequency = data_dict.get("frequency", None)
    try:
        # Check access - see authorisaton.py for implementation
        toolkit.check_access("report_schedule_list", context, {})
        if state and frequency:
            scheduled_reports = (
                model.Session.query(ReportSchedule)
                .filter_by(state=state)
                .filter_by(frequency=frequency)
                .all()
            )
        elif state:
            scheduled_reports = (
                model.Session.query(ReportSchedule)
                .filter_by(state=state)
                .all()
            )
        else:
            scheduled_reports = model.Session.query(ReportSchedule).all()
        return {
            "success": True,
            "result": [s.as_dict() for s in scheduled_reports],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@action("report_jobs")
@side_effect_free
def report_jobs(context, data_dict):
    error = "Invalid or no report schedule ID provided."

    report_schedule_id = data_dict.get("report_schedule_id", None)

    # Check to make sure `id` looks like a UUID
    if report_schedule_id and model.is_id(report_schedule_id):
        try:
            # Check access - see authorisaton.py for implementation
            toolkit.check_access("report_jobs", context, {})
            report_jobs = (
                model.Session.query(ReportJob)
                .filter_by(report_schedule_id=report_schedule_id)
                .all()
            )
            return [r.as_dict() for r in report_jobs]
        except Exception as e:
            error = str(e)

    return {"error": error}


@action("organisation_members")
def organisation_members(context, data_dict):
    """

    :param context:
    :param data_dict:
        A list of organisation names
    :return:
    """
    try:
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

        organisations = data_dict.get("organisations", [])
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

        try:
            toolkit.check_access("sysadmin", context, {})
        except toolkit.NotAuthorized:
            is_sysadmin = False
        else:
            is_sysadmin = True

        if is_sysadmin:
            # Show all members for sysadmin users
            members = (
                base_query.filter(_and_(*conditions))
                .join(Member, Member.group_id == Group.id)
                .join(User, User.id == Member.table_id)
                .order_by(Group.name.asc(), User.name.asc())
            )

            # log.debug(str(members))

            return members.all()
        else:
            toolkit.check_access("user_dashboard_reports", context, {})

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

    except Exception as e:
        log.error(str(e))


@action("report_schedule_delete")
@side_effect_free
def report_schedule_delete(context, data_dict):
    error = "Invalid or no report schedule ID provided."

    id = data_dict.get("id", None)

    # Check to make sure `id` looks like a UUID
    if id and model.is_id(id):
        try:
            toolkit.check_access("report_schedule_delete", context, {"id": id})

            # Load the record
            schedule = ReportSchedule.get(id)
            if schedule:
                # If a schedule has reports - mark it as deleted
                reports = toolkit.get_action("report_jobs")(
                    context, {"report_schedule_id": id}
                )
                if reports:
                    schedule.state = "deleted"
                    model.Session.add(schedule)
                # Otherwise delete the report schedule record entirely
                else:
                    model.Session.delete(schedule)
                model.Session.commit()
                return True
        except Exception as e:
            error = str(e)

    return {"errors": error}


@action("report_schedule_create")
@validate(schema.report_schedule_create)
def report_schedule_create(context, data_dict) -> bool:
    sess = context["session"]
    ctx = context.copy()
    ctx["ignore_auth"] = False

    toolkit.check_access("report_schedule_create", ctx, {})
    user = context["model"].User.get(context["user"])

    schedule = ReportSchedule(state="active", user_id=user.id, **data_dict)
    sess.add(schedule)
    sess.commit()
    return True

@action("report_job_create")
def report_job_create(context, data_dict):
    errors = {}
    try:
        validated_data_dict = toolkit.get_validator("report_job_validator")(
            data_dict, context
        )

        if validated_data_dict is data_dict:
            report_job_path = toolkit.config.get(
                "ckan.datavic_reporting.scheduled_reports_path"
            )
            org_id = data_dict.get("org_id")
            sub_org_ids = data_dict.get("sub_org_ids")
            organisation = (
                org_id
                if not sub_org_ids or sub_org_ids == "all-sub-organisations"
                else sub_org_ids
            )
            now = datetime.datetime.now()
            path_date = now.strftime("%Y") + "/" + now.strftime("%m")
            path = "{0}/{1}/{2}/".format(
                report_job_path, organisation, path_date
            )
            filename = "general_report_{0}.csv".format(now.isoformat())
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
            helpers.generate_general_report(
                path, filename, None, None, organisation
            )
            report_job.status = constants.Statuses.Generated
            model.Session.commit()

            user_emails = []
            if data_dict.get("user_roles"):
                for user_role in data_dict.get("user_roles").split(","):
                    role_emails = helpers.get_organisation_role_emails(
                        context, organisation, user_role
                    )
                    if role_emails:
                        user_emails.extend(role_emails)

            if data_dict.get("emails"):
                user_emails.extend(data_dict.get("emails").split(","))

            if user_emails and len(user_emails) > 0:
                extra_vars = {
                    "site_title": toolkit.config.get("ckan.site_title"),
                    "site_url": toolkit.config.get("ckan.site_url"),
                    "org_id": organisation,
                    "frequency": data_dict.get("frequency"),
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
            return {"success": True}
        else:
            errors = validated_data_dict
    except Exception as e:
        report_job.status = constants.Statuses.Failed
        model.Session.commit()
        log.error(e)
        errors["exception"] = str(e)

    return {"success": False, "error": errors}

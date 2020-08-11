import ckan.model as model
import ckan.plugins.toolkit as toolkit
import logging
import sqlalchemy
from ckan.logic import side_effect_free
from ckan.model.group import Group, Member
from ckan.model.user import User
from ckanext.datavic_reporting.report_models import ReportSchedule, ReportJob
from ckanext.datavic_reporting import authorisation, helpers
from sqlalchemy.orm import aliased

_and_ = sqlalchemy.and_
_session_ = model.Session
log = logging.getLogger(__name__)


@side_effect_free
def report_schedule_list(context, data_dict):
    state = data_dict.get('state', None)
    frequency = data_dict.get('frequency', None)
    try:
        # Check access - see authorisaton.py for implementation
        toolkit.check_access('report_schedule_list', context, {})
        if state and frequency:
            scheduled_reports = model.Session.query(ReportSchedule)\
                                                .filter_by(state=state)\
                                                .filter_by(frequency=frequency)\
                                                .all()
        elif state:
            scheduled_reports = model.Session.query(ReportSchedule).filter_by(state=state).all()
        else:
            scheduled_reports = model.Session.query(ReportSchedule).all()
        return [s.as_dict() for s in scheduled_reports]
    except Exception, e:
        return {'error': str(e)}


@side_effect_free
def report_jobs(context, data_dict):
    error = 'Invalid or no report schedule ID provided.'

    report_schedule_id = data_dict.get('report_schedule_id', None)

    # Check to make sure `id` looks like a UUID
    if report_schedule_id and model.is_id(report_schedule_id):
        try:
            # Check access - see authorisaton.py for implementation
            toolkit.check_access('report_jobs', context, {})
            report_jobs = model.Session.query(ReportJob).filter_by(report_schedule_id=report_schedule_id).all()
            return [r.as_dict() for r in report_jobs]
        except Exception, e:
            error = str(e)

    return {'error': error}


def organisation_members(context, organisations):
    """

    :param context:
    :param organisations: A list of organisation names
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
            Group.type == 'organization',
            Member.table_name == 'user'
        ]

        if len(organisations) > 0:
            conditions.append(Group.name.in_(organisations))

        if authorisation.is_sysadmin():
            # Show all members for sysadmin users
            return (
                base_query.filter(
                    _and_(
                        *conditions
                    )
                )
                .join(Member, Member.group_id == Group.id)
                .join(User, User.id == Member.table_id)
                .order_by(Group.name.asc(), User.name.asc())
            ).all()

        else:
            toolkit.check_access('user_dashboard_reports', context, {})

            # For authenticated users who are an admin of at least one organisation
            # only show members of organisations they are an admin of
            user = helpers.get_user()

            authenticated_member = aliased(Member, name='authenticated_member')
            authenticated_user = aliased(User, name='authenticated_user')

            # Only include organisations if authenticated user is an admin
            conditions.append(authenticated_member.table_name == 'user')
            conditions.append(authenticated_member.capacity == 'admin')
            conditions.append(authenticated_member.table_id == user.id)

            return (
                base_query.filter(
                    _and_(
                        *conditions
                    )
                )
                .join(Member, Member.group_id == Group.id)
                .join(User, User.id == Member.table_id)
                # Only include organisations if authenticated user is an admin
                .join(authenticated_member, authenticated_member.group_id == Group.id)
                .join(authenticated_user, authenticated_user.id == authenticated_member.table_id)
                .order_by(Group.name.asc(), User.name.asc())
            ).all()

    except Exception as e:
        log.error(str(e))

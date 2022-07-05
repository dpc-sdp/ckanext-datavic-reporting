import ckan.plugins.toolkit as toolkit
import ckan.authz as authz
import ckanext.datavic_reporting.helpers as helpers
import logging

log = logging.getLogger(__name__)


def is_sysadmin():
    user = helpers.get_user()
    return user and authz.is_sysadmin(user.name)


def has_user_permission_for_some_org(user_name, permission):
    return authz.has_user_permission_for_some_org(user_name, permission)


def user_dashboard_reports(context, data_dict=None):
    user = helpers.get_user()
    if not user:
        {"success": False, "msg": "Only logged in users can view reports."}

    # Sysadmin can do anything
    if is_sysadmin():
        return {"success": True}

    # Only users with at least 1 Admin access to an organisation can view reports
    if has_user_permission_for_some_org(user.name, "admin"):
        return {"success": True}

    return {
        "success": False,
        "msg": "Only user level admin or above can view reports.",
    }


def user_report_schedules(context, data_dict=None):
    user = helpers.get_user()
    if not user:
        {"success": False, "msg": "Only logged in users can view reports."}

    # Sysadmin can do anything
    if is_sysadmin():
        return {"success": True}

    return {
        "success": False,
        "msg": "Only user level sysadmin or above can view reports.",
    }


def report_schedule_create(context, data_dict):
    if is_sysadmin():
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can create report schedules.",
    }


def report_schedule_update(context, data_dict):
    if is_sysadmin():
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can update report schedules.",
    }


def report_schedule_delete(context, data_dict):
    if is_sysadmin():
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can delete report schedules.",
    }


def report_schedule_list(context, data_dict):
    if is_sysadmin():
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can view report schedules.",
    }


def report_jobs(context, data_dict):
    if is_sysadmin():
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can view report jobs.",
    }

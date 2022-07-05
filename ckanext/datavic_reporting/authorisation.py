import logging

import ckan.authz as authz
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


def has_user_permission_for_some_org(user_name, permission):
    return authz.has_user_permission_for_some_org(user_name, permission)


def user_dashboard_reports(context, data_dict=None):
    # Sysadmin can do anything
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}

    # Only users with at least 1 Admin access to an organisation can view reports
    if has_user_permission_for_some_org(context["user"], "admin"):
        return {"success": True}

    return {
        "success": False,
        "msg": "Only user level admin or above can view reports.",
    }


def user_report_schedules(context, data_dict=None):
    return authz.is_authorized("sysadmin", context)


def datavic_reporting_schedule_create(context, data_dict):
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can create report schedules.",
    }


def report_schedule_update(context, data_dict):
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can update report schedules.",
    }


def report_schedule_delete(context, data_dict):
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can delete report schedules.",
    }


def report_schedule_list(context, data_dict):
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can view report schedules.",
    }


def report_jobs(context, data_dict):
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can view report jobs.",
    }

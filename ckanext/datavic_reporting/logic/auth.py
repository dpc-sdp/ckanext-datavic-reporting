import logging

import ckan.authz as authz

from ckanext.toolbelt.decorators import Collector

auth, get_auth_functions = Collector("datavic_reporting").split()

log = logging.getLogger(__name__)


def has_user_permission_for_some_org(user_name, permission):
    return authz.has_user_permission_for_some_org(user_name, permission)


@auth("user_dashboard_reports")
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


@auth("user_report_schedules")
def user_report_schedules(context, data_dict=None):
    return authz.is_authorized("sysadmin", context)


@auth
def schedule_create(context, data_dict):
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can create report schedules.",
    }


@auth
def schedule_update(context, data_dict):
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can update report schedules.",
    }


@auth
def schedule_delete(context, data_dict):
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can delete report schedules.",
    }


@auth
def schedule_list(context, data_dict):
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can view report schedules.",
    }


@auth
def job_list(context, data_dict):
    if authz.is_authorized_boolean("sysadmin", context):
        return {"success": True}
    return {
        "success": False,
        "msg": "Only sysadmin user level can view report jobs.",
    }

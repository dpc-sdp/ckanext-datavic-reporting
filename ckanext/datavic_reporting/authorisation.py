import ckan.plugins.toolkit as toolkit
import ckan.authz as authz
import helpers
import logging

log = logging.getLogger(__name__)


def is_sysadmin():
    user = helpers.get_user()
    return user and authz.is_sysadmin(user.name)

def has_user_permission_for_some_org(user_name, permission):
    return authz.has_user_permission_for_some_org(user_name, permission)

def user_dashboard_reports(context, data_dict=None):
    log.debug('user_dashboard_reports')
    user = helpers.get_user()
    if not user:
        {'success': False, 'msg': 'Only logged in users can view reports.'}

    # Sysadmin can do anything
    if is_sysadmin():
        return {'success': True}

    # Only users with at least 1 Admin access to an organisation can view reports
    if has_user_permission_for_some_org(user.name, 'admin'):
        return {'success': True}

    return {'success': False, 'msg': 'Only user level admin or above can view reports.'}

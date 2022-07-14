from ckan.logic.schema import validator_args


@validator_args
def schedule_create(
    not_missing,
    one_of,
    group_id_or_name_exists,
    ignore_empty,
    datavic_reporting_sub_org_ids,
    frequency_validator,
    user_roles_validator,
    emails_validator,
    ignore,
    ignore_not_sysadmin,
    ignore_missing,
    convert_user_name_or_id_to_id,
):
    return {
        "user_id": [
            ignore_missing,
            ignore_not_sysadmin,
            convert_user_name_or_id_to_id,
        ],
        "report_type": [not_missing, one_of(["general"])],
        "org_id": [not_missing, group_id_or_name_exists],
        "sub_org_ids": [ignore_empty, datavic_reporting_sub_org_ids],
        "frequency": [not_missing, frequency_validator],
        "user_roles": [not_missing, user_roles_validator],
        "emails": [not_missing, emails_validator],
        "__extras": [ignore],
        "__junk": [ignore],
    }


@validator_args
def schedule_update(
    not_missing,
    frequency_validator,
    user_roles_validator,
    emails_validator,
    ignore,
    ignore_missing,
    unicode_safe,
):
    return {
        "id": [not_missing, unicode_safe],
        "frequency": [ignore_missing, frequency_validator],
        "user_roles": [ignore_missing, user_roles_validator],
        "emails": [ignore_missing, emails_validator],
        "__extras": [ignore],
        "__junk": [ignore],
    }


@validator_args
def schedule_list(ignore_missing, unicode_safe):
    return {
        "frequency": [ignore_missing, unicode_safe],
        "state": [ignore_missing, unicode_safe],
    }


@validator_args
def job_list(not_missing, unicode_safe):
    return {
        "report_schedule_id": [not_missing, unicode_safe],
    }


@validator_args
def job_create(
    not_missing,
    group_id_or_name_exists,
    ignore_empty,
    datavic_reporting_sub_org_ids,
    frequency_validator,
    user_roles_validator,
    emails_validator,
    ignore,
    unicode_safe,
):
    return {
        "org_id": [ignore_empty, group_id_or_name_exists],
        "sub_org_ids": [ignore_empty, datavic_reporting_sub_org_ids],
        "id": [not_missing, unicode_safe],
        "frequency": [not_missing, frequency_validator],
        "user_roles": [not_missing, user_roles_validator],
        "emails": [not_missing, emails_validator],
        "__extras": [ignore],
        "__junk": [ignore],
    }

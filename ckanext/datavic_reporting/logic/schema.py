from ckan.logic.schema import validator_args

@validator_args
def datavic_reporting_schedule_create(not_missing, one_of, group_id_or_name_exists, ignore_empty, datavic_reporting_sub_org_ids, frequency_validator, user_roles_validator, emails_validator, ignore, ignore_not_sysadmin, ignore_missing, convert_user_name_or_id_to_id):
    return {
        "user_id": [ignore_missing, ignore_not_sysadmin, convert_user_name_or_id_to_id],
        "report_type": [not_missing, one_of(["general"])],
        "org_id": [not_missing, group_id_or_name_exists],
        "sub_org_ids": [ignore_empty, datavic_reporting_sub_org_ids],

        "frequency": [not_missing, frequency_validator],
        "user_roles": [not_missing, user_roles_validator],
        "emails": [not_missing, emails_validator],
        "__extras": [ignore],
        "__junk": [ignore],
    }

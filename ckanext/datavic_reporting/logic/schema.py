from ckan.logic.schema import validator_args

@validator_args
def report_schedule_create(not_missing, one_of, group_id_or_name_exists, json_list_or_string, default, datavic_reporting_sub_org_ids, frequency_validator, user_roles_validator, emails_validator, ignore):
    return {
        "report_type": [not_missing, one_of(["general"])],
        "org_id": [not_missing, group_id_or_name_exists],
        "sub_org_ids": [default("[]"), json_list_or_string, datavic_reporting_sub_org_ids],

        "frequency": [not_missing, frequency_validator],
        "user_roles": [not_missing, user_roles_validator],
        "emails": [not_missing, emails_validator],
        "__extras": [ignore],
        "__junk": [ignore],
    }

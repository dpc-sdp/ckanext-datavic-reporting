import pytest

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action

@pytest.mark.usefixtures("with_plugins", "clean_db", "with_request_context")
class TestScheduleCreate:
    def test_basic(self, organization, faker, sysadmin):
        result = call_action(
            "report_schedule_create",
            {"user": sysadmin["name"]},
            report_type="general",
            org_id=organization["id"],
            frequency="monthly",
            user_roles="member",
            emails=faker.email(),
        )

        assert result is True

        items = call_action(
            "report_schedule_list",
        )

        assert len(items["result"]) == 1
        assert items["result"][0]["user_id"] == sysadmin["id"]

    @pytest.mark.parametrize(
        "field", ["report_type", "org_id", "frequency", "user_roles", "emails"]
    )
    def test_validation(self, field, organization, faker, sysadmin):
        data = dict(
            report_type="general",
            org_id=organization["id"],
            frequency="monthly",
            user_roles="member",
            emails=faker.email(),
        )
        data.pop(field)

        with pytest.raises(tk.ValidationError) as err:
            call_action(
                "report_schedule_create", {"user": sysadmin["name"]}, **data
            )

        assert field in err.value.error_dict
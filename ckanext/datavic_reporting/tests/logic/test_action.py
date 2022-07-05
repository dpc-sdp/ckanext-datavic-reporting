import pytest

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestScheduleCreate:
    def test_basic(self, organization, faker, sysadmin):
        result = call_action(
            "datavic_reporting_schedule_create",
            {"user": sysadmin["name"]},
            report_type="general",
            org_id=organization["id"],
            frequency="monthly",
            user_roles="member",
            emails=faker.email(),
        )

        assert result["user_id"] == sysadmin["id"]

        items = call_action(
            "report_schedule_list",
        )

        assert len(items["result"]) == 1
        assert items["result"][0]["user_id"] == sysadmin["id"]

    def test_factory(self, report_schedule):
        items = call_action("report_schedule_list")
        assert items["result"] == [report_schedule]

    def test_factory_with_controlled_user(self, report_schedule_factory, user):
        result = report_schedule_factory(user_id=user["id"])
        assert result["user_id"] == user["id"]

    @pytest.mark.parametrize(
        "field", ["report_type", "org_id", "frequency", "user_roles", "emails"]
    )
    def test_validation(self, field, organization, faker):
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
                "datavic_reporting_schedule_create",  **data
            )

        assert field in err.value.error_dict

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestScheduleUpdate:
    def test_basic(self, report_schedule):
        pass

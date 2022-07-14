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
            "datavic_reporting_schedule_list",
        )

        assert len(items) == 1
        assert items[0]["user_id"] == sysadmin["id"]

    def test_factory(self, report_schedule):
        items = call_action("datavic_reporting_schedule_list")
        assert items == [report_schedule]

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
            call_action("datavic_reporting_schedule_create", **data)

        assert field in err.value.error_dict


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestScheduleUpdate:
    def test_missing_id(self):
        with pytest.raises(tk.ValidationError):
            call_action("datavic_reporting_schedule_update")

    def test_invalid_id(self):
        with pytest.raises(tk.ObjectNotFound):
            call_action("datavic_reporting_schedule_update", id="not-real")

    def test_update(self, report_schedule, faker):
        email = faker.email()
        result = call_action(
            "datavic_reporting_schedule_update",
            id=report_schedule["id"],
            emails=email,
        )
        assert result["emails"] == email


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestScheduleList:
    def test_list_empty(self):
        result = call_action("datavic_reporting_schedule_list")
        assert result == []

    def test_list_all(self, report_schedule_factory):
        report_schedule_factory()
        report_schedule_factory()

        result = call_action("datavic_reporting_schedule_list")
        assert len(result) == 2

    def test_by_frequency(self, report_schedule_factory):
        daily = report_schedule_factory(frequency="daily")
        monthly = report_schedule_factory(frequency="monthly")

        result = call_action(
            "datavic_reporting_schedule_list", frequency="daily"
        )
        assert result == [daily]

        result = call_action(
            "datavic_reporting_schedule_list", frequency="monthly"
        )
        assert result == [monthly]

    def test_by_state(self, report_schedule_factory):
        active = report_schedule_factory()

        result = call_action("datavic_reporting_schedule_list", state="active")
        assert result == [active]

        result = call_action(
            "datavic_reporting_schedule_list", state="pending"
        )
        assert result == []


@pytest.mark.usefixtures("with_plugins", "clean_db", "with_request_context")
class TestJobCreate:
    def test_basic(self, faker, report_schedule, sysadmin, organization):
        call_action(
            "datavic_reporting_job_create",
            {"user": sysadmin["name"]},
            id=report_schedule["id"],
            org_id=organization["id"],
            frequency="monthly",
            user_roles="member",
            emails=faker.email(),
        )

        items = call_action(
            "datavic_reporting_job_list",
            report_schedule_id=report_schedule["id"],
        )

        assert len(items) == 1

    def test_factory(self, report_job):
        items = call_action(
            "datavic_reporting_job_list",
            report_schedule_id=report_job["report_schedule_id"],
        )
        assert items == [report_job]

    @pytest.mark.parametrize("field", ["frequency", "user_roles", "emails"])
    def test_validation(self, field, faker, report_schedule):
        data = dict(
            report_type="general",
            frequency="monthly",
            user_roles="member",
            emails=faker.email(),
            report_schedule_id=report_schedule["id"],
        )
        data.pop(field)

        with pytest.raises(tk.ValidationError) as err:
            call_action("datavic_reporting_job_create", **data)

        assert field in err.value.error_dict


@pytest.mark.usefixtures("with_plugins", "clean_db", "with_request_context")
class TestJobList:
    def test_missing_id(self):
        with pytest.raises(tk.ValidationError):
            call_action("datavic_reporting_job_list")

    def test_list_not_real(self):
        result = call_action(
            "datavic_reporting_job_list", report_schedule_id="not-real"
        )
        assert result == []

    def test_list_empty(self, report_schedule):
        result = call_action(
            "datavic_reporting_job_list",
            report_schedule_id=report_schedule["id"],
        )
        assert result == []

    def test_all(self, report_job_factory, report_schedule):
        first = report_job_factory(id=report_schedule["id"])
        seond = report_job_factory(id=report_schedule["id"])
        report_job_factory()

        result = call_action(
            "datavic_reporting_job_list",
            report_schedule_id=report_schedule["id"],
        )
        assert len(result) == 2

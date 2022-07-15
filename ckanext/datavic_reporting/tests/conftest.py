import factory
import pytest
from ckan.tests import factories, helpers
from pytest_factoryboy import register

from ckanext.datavic_reporting.model import ReportJob, ReportSchedule


@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("datavic_reporting")


class OrganizationFactory(factories.Organization):
    pass


register(OrganizationFactory, "organization")


@register
class UserFactory(factories.User):
    pass


class SysadminFactory(factories.Sysadmin):
    pass


register(SysadminFactory, "sysadmin")


@register
class ReportScheduleFactory(factory.Factory):
    """A factory class for creating CKAN datasets."""

    class Meta:
        model = ReportSchedule

    report_type = "general"
    org_id = factory.LazyFunction(lambda: OrganizationFactory()["id"])
    user_id = factory.LazyFunction(lambda: SysadminFactory()["id"])
    sub_org_ids = None
    frequency = "daily"
    user_roles = "admin"
    emails = factory.Faker("email")
    state = "active"
    last_completed = None

    @classmethod
    def _build(cls, target_class, *args, **kwargs):
        raise NotImplementedError(".build() isn't supported")

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        if args:
            assert False, "Positional args aren't supported, use keyword args."

        context = {"user": factories._get_action_user_name(kwargs)}

        return helpers.call_action(
            "datavic_reporting_schedule_create", context=context, **kwargs
        )


@register
class ReportJobFactory(factory.Factory):
    """A factory class for creating CKAN datasets."""

    class Meta:
        model = ReportJob

    id = factory.LazyFunction(lambda: ReportScheduleFactory()["id"])
    org_id = factory.LazyFunction(lambda: OrganizationFactory()["id"])

    frequency = "daily"
    user_roles = "admin"
    emails = factory.Faker("email")

    @classmethod
    def _build(cls, target_class, *args, **kwargs):
        raise NotImplementedError(".build() isn't supported")

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        if args:
            assert False, "Positional args aren't supported, use keyword args."

        context = {"user": factories._get_action_user_name(kwargs)}
        return helpers.call_action(
            "datavic_reporting_job_create", context=context, **kwargs
        )

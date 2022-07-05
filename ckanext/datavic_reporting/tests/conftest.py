import pytest
from pytest_factoryboy import register

from ckan.tests import factories

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

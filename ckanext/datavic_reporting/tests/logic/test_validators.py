from unittest.mock import ANY

import pytest

import ckan.plugins.toolkit as tk

from ckanext.datavic_reporting.logic.validators import *


@pytest.mark.usefixtures("with_plugins")
class TestReportType:
    def test_valid(self):
        data, errors = tk.navl_validate(
            {"value": "general"}, {"value": [report_type]}
        )

        assert data == {"value": "general"}
        assert not errors

    def test_invalid(self):
        data, errors = tk.navl_validate(
            {"value": "not-general"}, {"value": [report_type]}
        )

        assert data == {"value": "not-general"}
        assert errors == {"value": [ANY]}

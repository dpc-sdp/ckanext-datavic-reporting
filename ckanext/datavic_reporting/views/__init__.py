from .member_report import member_report
from .reporting import reporting
from .scheduling import scheduling


def get_blueprints():
    return [scheduling, reporting, member_report]

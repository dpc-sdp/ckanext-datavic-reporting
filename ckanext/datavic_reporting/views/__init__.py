from .scheduling import scheduling
from .reporting import reporting
from .member_report import member_report

def get_blueprints():
    return [
        scheduling, reporting, member_report
    ]

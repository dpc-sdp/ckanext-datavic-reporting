import datetime

import ckan.model as model
from ckan.lib.base import *
from ckan.model.types import make_uuid
from sqlalchemy import Column, ForeignKey, MetaData, Table, types
from sqlalchemy.orm import mapper, relation

log = __import__("logging").getLogger(__name__)

metadata = MetaData()


class ReportSchedule(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = make_uuid()
        self.timestamp = datetime.datetime.utcnow()

    @classmethod
    def get(self, id):
        return model.Session.query(self).filter_by(id=id).first()

    def as_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "report_type": self.report_type,
            "org_id": self.org_id,
            "sub_org_ids": self.sub_org_ids,
            "frequency": self.frequency,
            "user_roles": self.user_roles,
            "emails": self.emails,
            "state": self.state,
            "last_completed": self.last_completed.isoformat()
            if self.last_completed
            else "",
            "user_id": self.user_id,
        }


report_schedule_table = Table(
    "report_schedule",
    metadata,
    Column("id", types.UnicodeText, primary_key=True, default=make_uuid),
    Column("timestamp", types.DateTime, default=datetime.datetime.utcnow()),
    Column("user_id", types.UnicodeText),
    Column("report_type", types.UnicodeText),
    Column("org_id", types.UnicodeText),
    Column("sub_org_ids", types.UnicodeText),
    Column("frequency", types.UnicodeText),
    Column("user_roles", types.UnicodeText),
    Column("emails", types.UnicodeText),
    Column("state", types.UnicodeText),
    Column("last_completed", types.DateTime),
)

mapper(ReportSchedule, report_schedule_table)


class ReportJob(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = make_uuid()
        self.timestamp = datetime.datetime.utcnow()

    @classmethod
    def get(self, id):
        return model.Session.query(self).filter_by(id=id).first()

    def as_dict(self):
        return {
            "id": self.id,
            "report_schedule_id": self.report_schedule_id,
            "timestamp": self.timestamp.isoformat(),
            "filename": self.filename,
            "frequency": self.frequency,
            "user_roles": self.user_roles,
            "emails": self.emails,
            "status": self.status,
        }


report_job_table = Table(
    "report_job",
    metadata,
    Column("id", types.UnicodeText, primary_key=True, default=make_uuid),
    Column("report_schedule_id", types.UnicodeText),
    Column("timestamp", types.DateTime, default=datetime.datetime.utcnow()),
    Column("filename", types.UnicodeText),
    Column("frequency", types.UnicodeText),
    Column("user_roles", types.UnicodeText),
    Column("emails", types.UnicodeText),
    # status: scheduled -> processing -> generated -> completed
    Column("status", types.UnicodeText),
)

mapper(ReportJob, report_job_table)


def init_tables():
    metadata.create_all(model.meta.engine)

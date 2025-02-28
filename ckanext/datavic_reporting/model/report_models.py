from __future__ import annotations

import datetime

from sqlalchemy import Column, types

import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.model.types import make_uuid


log = __import__("logging").getLogger(__name__)


class ReportSchedule(tk.BaseModel):
    __tablename__ = "report_schedule"

    id = Column(types.UnicodeText, primary_key=True, default=make_uuid)
    timestamp = Column(types.DateTime, default=datetime.datetime.utcnow)
    user_id = Column(types.UnicodeText)
    report_type = Column(types.UnicodeText)
    org_id = Column(types.UnicodeText)
    sub_org_ids = Column(types.UnicodeText)
    frequency = Column(types.UnicodeText)
    user_roles = Column(types.UnicodeText)
    emails = Column(types.UnicodeText)
    state = Column(types.UnicodeText)
    last_completed = Column(types.DateTime)

    @classmethod
    def get(cls, id):
        return model.Session.query(cls).filter_by(id=id).one_or_none()

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


class ReportJob(tk.BaseModel):
    __tablename__ = "report_job"

    id = Column(types.UnicodeText, primary_key=True, default=make_uuid)
    report_schedule_id = Column(types.UnicodeText)
    timestamp = Column(types.DateTime, default=datetime.datetime.utcnow)
    filename = Column(types.UnicodeText)
    frequency = Column(types.UnicodeText)
    user_roles = Column(types.UnicodeText)
    emails = Column(types.UnicodeText)
    status = Column(types.UnicodeText)

    @classmethod
    def get(cls, id):
        return model.Session.query(cls).filter_by(id=id).one_or_none()

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

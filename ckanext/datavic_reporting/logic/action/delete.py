import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.logic import side_effect_free

from ckanext.datavic_reporting.model import ReportSchedule


@side_effect_free
def report_schedule_delete(context, data_dict):
    error = "Invalid or no report schedule ID provided."

    id = data_dict.get("id", None)

    # Check to make sure `id` looks like a UUID
    if id and model.is_id(id):
        try:
            toolkit.check_access("report_schedule_delete", context, {"id": id})

            # Load the record
            schedule = ReportSchedule.get(id)
            if schedule:
                # If a schedule has reports - mark it as deleted
                reports = toolkit.get_action("report_jobs")(
                    context, {"report_schedule_id": id}
                )
                if reports:
                    schedule.state = "deleted"
                    model.Session.add(schedule)
                # Otherwise delete the report schedule record entirely
                else:
                    model.Session.delete(schedule)
                model.Session.commit()
                return True
        except Exception as e:
            error = str(e)

    return {"errors": error}

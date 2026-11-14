from modules.calendar_connector import get_service
import datetime

class CalendarAgent:
    def __init__(self):
        self.service = get_service()
        print("CalendarAgent Initialized ✔")

    def create_meeting(self, title, time_str, duration_min=30):
        start_time = datetime.datetime.fromisoformat(time_str)
        end_time = start_time + datetime.timedelta(minutes=duration_min)

        event = {
            "summary": title,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Kolkata"},
        }

        created = self.service.events().insert(calendarId="primary", body=event).execute()
        return {"status": "created", "id": created.get("id")}

    def list_upcoming(self, limit=5):
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        events = self.service.events().list(calendarId="primary", timeMin=now, maxResults=limit).execute()
        return events.get("items", [])

    def update_event(self, event_id, new_title):
        event = self.service.events().get(calendarId="primary", eventId=event_id).execute()
        event["summary"] = new_title
        updated = self.service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
        return {"status": "updated", "title": updated.get("summary")}

    def delete_event(self, event_id):
        self.service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {"status": "deleted"}


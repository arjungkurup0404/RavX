import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ===== CONFIG =====
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_PATH = "config/token.json"


def get_calendar_service():
    """
    Loads Google Calendar service using OAuth token
    generated via Web OAuth flow.
    """
    if not os.path.exists(TOKEN_PATH):
        raise Exception("Google OAuth not completed. Visit /auth/google first.")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build("calendar", "v3", credentials=creds)


def create_event(title: str, description: str):
    """
    Creates a Google Calendar event with Google Meet link.
    """
    service = get_calendar_service()

    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(minutes=60)

    event_body = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat() + "Z",
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time.isoformat() + "Z",
            "timeZone": "UTC",
        },
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{int(start_time.timestamp())}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    event = service.events().insert(
        calendarId="primary",
        body=event_body,
        conferenceDataVersion=1,
    ).execute()

    meet_link = None
    entry_points = event.get("conferenceData", {}).get("entryPoints", [])
    if entry_points:
        meet_link = entry_points[0].get("uri")

    return {
        "status": "event_created",
        "event_id": event.get("id"),
        "meet_link": meet_link,
    }

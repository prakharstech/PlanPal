# backend/calendar.py

import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()  # Load from .env

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = "creds.json"
CALENDAR_ID = os.getenv("CALENDAR_ID")

# Authenticate and build service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)


def list_upcoming_events():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events = []
    page_token = None

    while True:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now,
            singleEvents=True,
            orderBy="startTime",
            pageToken=page_token
        ).execute()

        events.extend(events_result.get("items", []))
        page_token = events_result.get("nextPageToken")

        if not page_token:
            break

    return events



def book_event(summary, start_time, end_time, description=""):
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
    }

    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created_event


def delete_event(event_id):
    try:
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        return f"Event with ID '{event_id}' deleted successfully."
    except Exception as e:
        return f"Failed to delete event: {e}"


def reschedule_event(event_id, new_start, new_end):
    try:
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

        # Update the times
        event["start"]["dateTime"] = new_start
        event["end"]["dateTime"] = new_end
        event["start"]["timeZone"] = "Asia/Kolkata"
        event["end"]["timeZone"] = "Asia/Kolkata"

        updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()
        return f"Event rescheduled: {updated_event.get('htmlLink')}"
    except Exception as e:
        return f"Failed to reschedule event: {e}"

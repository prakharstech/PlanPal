# backend/calendar_utils.py
import datetime
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service(token: str):
    """Builds a Calendar service object from a user's access token."""
    try:
        # The token received here is now a valid access token
        creds = Credentials(token=token, scopes=SCOPES)
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to create calendar service: {e}")
        return None


def list_upcoming_events(service):
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events = []
    page_token = None
    try:
        while True:
            events_result = service.events().list(
                calendarId='primary', # 'primary' refers to the user's main calendar
                timeMin=now,
                singleEvents=True,
                orderBy="startTime",
                pageToken=page_token
            ).execute()
            events.extend(events_result.get("items", []))
            page_token = events_result.get("nextPageToken")
            if not page_token:
                break
    except HttpError as e:
        print(f"An error occurred: {e}")
        return []
    return events

def book_event(service, summary, start_time, end_time, description=""):
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
    }
    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event
    except HttpError as e:
        return {"error": f"Failed to book event: {e}"}


def delete_event(service, event_id):
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"Event with ID '{event_id}' deleted successfully."
    except HttpError as e:
        return f"Failed to delete event: {e}"

def reschedule_event(service, event_id, new_start, new_end):
    try:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        event["start"]["dateTime"] = new_start
        event["end"]["dateTime"] = new_end
        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return f"Event rescheduled: {updated_event.get('htmlLink')}"
    except HttpError as e:
        return f"Failed to reschedule event: {e}"
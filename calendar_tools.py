import os
from datetime import datetime, timedelta
import google_auth_oauthlib.flow

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Calendar scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# 🔴 ABSOLUTE PATH TO credentials.json
CREDENTIALS_PATH = r"D:\yash\meeting-coordinator\meeting-coordinator\credentials.json"
TOKEN_PATH = "token.json"


def get_calendar_service():
    """
    Authenticates user and returns Google Calendar service
    """
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # If no valid credentials, login again
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # ✅ THIS IS WHERE YOUR LINE GOES
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for next run
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service


def create_calendar_event(title, attendees, start_time, duration_minutes=60):
    """
    Creates a Google Calendar event and sends invites
    """
    service = get_calendar_service()

    end_time = start_time + timedelta(minutes=duration_minutes)

    event = {
        "summary": title,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "attendees": [{"email": email} for email in attendees],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 1440},
                {"method": "popup", "minutes": 30},
            ],
        },
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event,
        sendUpdates="all"
    ).execute()

    return created_event


def list_upcoming_events(max_results=10):
    """
    Lists upcoming Google Calendar events
    """
    service = get_calendar_service()

    now = datetime.utcnow().isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return events_result.get("items", [])

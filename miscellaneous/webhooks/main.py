from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
import os
import pickle
from typing import Optional
import json
import pytz

app = FastAPI()

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class MeetingRequest(BaseModel):
    agenda: str
    email: str
    time: str  # Expected format: "YYYY-MM-DD HH:MM"
    timezone: str  # Example: "America/New_York", "Europe/London", "Asia/Kolkata"
    short_bio: str

def get_calendar_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            if not os.path.exists('credentials.json'):
                raise HTTPException(
                    status_code=500,
                    detail="""Google Calendar credentials not found. Please follow these steps:
                    1. Go to Google Cloud Console (https://console.cloud.google.com/)
                    2. Create a new project or select an existing one
                    3. Enable the Google Calendar API
                    4. Create OAuth 2.0 credentials (Desktop app)
                    5. Download the credentials and save as 'credentials.json' in this directory"""
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

@app.post("/webhook/eleven-labs")
async def eleven_labs_webhook(request: Request):
    try:
        data = await request.json()
        meeting_request = MeetingRequest(**data)
        
        # Parse the time string into a datetime object
        meeting_time = datetime.strptime(meeting_request.time, "%Y-%m-%d %H:%M")
        
        # Set the timezone
        try:
            timezone = pytz.timezone(meeting_request.timezone)
            meeting_time = timezone.localize(meeting_time)
        except pytz.exceptions.UnknownTimeZoneError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid timezone: {meeting_request.timezone}. Please use a valid timezone like 'America/New_York', 'Europe/London', or 'Asia/Kolkata'"
            )
        
        # Create calendar event
        service = get_calendar_service()
        
        event = {
            'summary': f'Meeting with {meeting_request.email}',
            'description': f'Agenda: {meeting_request.agenda}\nBio: {meeting_request.short_bio}',
            'start': {
                'dateTime': meeting_time.isoformat(),
                'timeZone': meeting_request.timezone,
            },
            'end': {
                'dateTime': (meeting_time + timedelta(hours=1)).isoformat(),
                'timeZone': meeting_request.timezone,
            },
            'attendees': [
                {'email': meeting_request.email},
            ],
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        
        return {
            "status": "success",
            "message": "Meeting scheduled successfully",
            "event_id": event.get('id'),
            "timezone": meeting_request.timezone
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

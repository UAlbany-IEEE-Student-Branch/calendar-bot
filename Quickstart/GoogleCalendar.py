from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import datetime
import os
import os.path
from dateutil.relativedelta import relativedelta
import json


def access_google_calendar() -> object:
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('Quickstart/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def process_weekly_events(service: object) -> str:

    # Call the Calendar API
    today = datetime.datetime.today()
    week_from_now = today + relativedelta(days=12, hours=23, minutes=59, seconds=59)
    tmax = week_from_now.isoformat('T') + 'Z'
    tmin = today.isoformat('T') + 'Z'

    json_file_name = tmin[:tmin.index('T')]

    events_result = service.events().list(
        calendarId='primary',
        timeMin=tmin,
        timeMax=None,
        singleEvents=True,
        orderBy='startTime').execute()

    events = events_result.get('items', [])

    if events:
        os.chdir("./json_weekly_files")
        with open(f"{json_file_name}.json", 'w', encoding='utf-8') as f:
            event_list = {}
            for i, event in enumerate(events):
                event_entry = {"event_name": event['summary'], "start_time": event['start']['dateTime'],
                               "end_time": event['end']['dateTime'], "location": "void"}
                event_list[f"Event No.{i+1}"] = event_entry
            json.dump(event_list, fp=f, indent=4)
    f.close()
    os.chdir("..")

    return f"{json_file_name}.json"
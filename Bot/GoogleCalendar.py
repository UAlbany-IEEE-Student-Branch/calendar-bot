from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import datetime
import os
import os.path
import dateutil.parser
from dateutil.relativedelta import relativedelta
import json


def access_google_calendar() -> object:
    """This function is used to access the Google Calendar API and returns an object that is used to interact
    with said API"""
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def process_weekly_events(service: object) -> str:
    """This function calls access_google_calendar() and uses the permission to interact with the google calendar API
    in order to generate a .json file with the weekly events scheduled for the UAlbany IEEE; the function also returns
    the name of the file generated"""
    today = datetime.datetime.today()
    week_from_now = today + relativedelta(days=6, hours=23, minutes=59, seconds=59)
    tmax = week_from_now.isoformat('T') + 'Z'
    tmin = today.isoformat('T') + 'Z'

    json_file_name = tmin[:tmin.index('T')]

    events_result = service.events().list(
        calendarId='primary',
        timeMin=tmin,
        timeMax=tmax,
        singleEvents=True,
        orderBy='startTime').execute()

    events = events_result.get('items', [])

    if events:
        os.chdir("./json_weekly_files")
        with open(f"{json_file_name}.json", 'w', encoding='utf-8') as f:
            event_list = {}
            time_format = "%U:%w:%H:%M:%S"
            clock_time_format = "%I:%M %p"
            for i, event in enumerate(events):
                start_time = dateutil.parser.parse(event['start']['dateTime'])
                start_time_listable = start_time.strftime(clock_time_format)
                end_time = dateutil.parser.parse(event['end']['dateTime'])
                end_time_listable = end_time.strftime(clock_time_format)
                start_time_parse = start_time.strftime(time_format)
                start_time_listable, end_time_listable, start_time_parse = \
                    str(start_time_listable), str(end_time_listable), str(start_time_parse)

                event_entry = {"event_name": None if not event.get('summary') else event['summary'],
                               "description": None if not event.get('description') else event['description'],
                               "start_time": start_time_listable, "end_time": end_time_listable,
                               "location": None if not event.get('location') else event['location'],
                               "start_time_parse": start_time_parse}

                event_list[f"Event No.{i+1}"] = event_entry
            json.dump(event_list, fp=f, indent=4)
        f.close()
        os.chdir("..")
    else:
        return None
    return f"./json_weekly_files/{json_file_name}.json"
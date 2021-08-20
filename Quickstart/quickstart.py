from __future__ import print_function

import discord 
from discord.ext import commands
from discord.ext.commands.bot import Bot
from dotenv import load_dotenv
import os
from dateutil.relativedelta import relativedelta
import json


load_dotenv('.env')
TOKEN = os.getenv("IEEE_Bot")

import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
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

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    today = datetime.datetime.today()
    week_from_now = today + relativedelta(days=6, hours=23, minutes=59, seconds=59)
    tmin = week_from_now.isoformat('T') + 'Z'
    tmax = today.isoformat('T') + 'Z'

    json_file_name = tmin[:tmin.index('T')]

    events_result = service.events().list(
        calendarId='primary',
        timeMin=tmin,
        timeMax=tmax,
        singleEvents=True,
        orderBy='startTime').execute()

    events = events_result.get('items', [])

    os.chdir("./json_weekly_files")
    with open(f"{json_file_name}.json", 'w', encoding='utf-8') as f:
        event_list = {}
        for i, event in enumerate(events):
            event_entry = {"event_name": event['summary'], "start_time": event['start']['dateTime'],
                           "end_time": event['end']['dateTime'], "location": "void"}
            event_list[f"Event No.{i+1}"] = event_entry
        json.dump(event_list, fp=f, indent=4)


if __name__ == '__main__':
    main()

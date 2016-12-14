from __future__ import print_function
import httplib2
import os
import pprint

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from calendar import monthrange
import datetime
import dateutil.parser
from datetime import date,timedelta

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def GetCredentials():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service

def getTime():
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    return now

def getStartTime():
    B3 = datetime.datetime(date.today().year,1,1)
    now = B3.isoformat() + 'Z'
    return now

def getStartAndEndOfMonth(year,month):
    Range = monthrange(year, month)
    LDOM = Range[1]
    startM = datetime.datetime(year,month,1).isoformat() + 'Z'
    endM = datetime.datetime(year,month,LDOM).isoformat() + 'Z'
    print(startM,endM)
    return [startM,endM]

def GetEvents(year,month):
    now = getStartAndEndOfMonth(year,month)
    service = GetCredentials()
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now[0], timeMax=now[1], maxResults=2500, singleEvents=True,
        orderBy='startTime').execute()
    lis = []
    for i in eventsResult['items']:
        _summary = i['summary']
        _id = i['iCalUID']
        _link = i['htmlLink']
        try:
            _description = i['description']
        except Exception:
            _description = ''
        _creator = i['creator']
        _allDay = False
        try:
            _allDayDate = dateutil.parser.parse(i['start']['date'])
            _allDay = True
            _dt1 = _allDayDate
            _dt2 = _allDayDate
        except Exception:
            _dt1 = dateutil.parser.parse(i['start']['dateTime'])
            _dt2 = dateutil.parser.parse(i['end']['dateTime'])
        event = {}
        event['summary'] = _summary
        event['id'] = _id
        event['link'] = _link
        event['description'] = _description
        event['creator'] = _creator
        event['starttime'] = _dt1
        event['endtime'] = _dt2
        event['allday'] = _allDay
        lis.append(event) 
    return lis 
        

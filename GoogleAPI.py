from __future__ import print_function
import httplib2
import os
import pprint

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from collections import defaultdict
from calendar import monthrange
import datetime
import dateutil.parser
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
from calendarEvent import CalendarEvent as CE


class GoogleAPI:
    def __init__(self):
        self.flags = self.getFlags()
        self.SCOPES = 'https://www.googleapis.com/auth/calendar'
        self.CLIENT_SECRET_FILE = 'client_secret.json'
        self.APPLICATION_NAME = 'Google Calendar API Python Quickstart'
        self.credentials = self.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
       # self.service = discovery.build('calendar', 'v3', http=self.http)
        self.service = self.getService()
        self.eventsResult = self.Get12MonthEvents()
        #print(self.service)

    def getFlags(self):
        try:
            import argparse
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        except ImportError:
            flags = None
        return flags

    def get_credentials(self):
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
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def getService(self):
        #credentials = get_credentials()
        http = self.credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        return service

    def getTime(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        return now

    def getStartTime(self):
        B3 = datetime.datetime(date.today().year,1,1)
        now = B3.isoformat() + 'Z'
        return now

    def getStartAndEndOfMonth(self,year,month):
        Range = monthrange(year, month)
        LDOM = Range[1]
        startM = datetime.datetime(year,month,1).isoformat() + 'Z'
        endM = datetime.datetime(year,month,LDOM).isoformat() + 'Z'
        return [startM,endM]

##    def GetEvents(self,year,month,service):
##        now = getStartAndEndOfMonth(year,month)
##        eventsResult = self.service.events().list(
##            calendarId='primary', timeMin=now[0], timeMax=now[1], maxResults=2500, singleEvents=True,
##            orderBy='startTime').execute()
##        return eventsResult

    def Get12MonthEvents(self):
        firstdayofCurrMonth = date.today().replace(day=1)
        MonthBegin = firstdayofCurrMonth + relativedelta(months=- 12)
        YEAR = MonthBegin.year
        MONTH = MonthBegin.month
        DATE = datetime.datetime(YEAR,1,1).isoformat() + 'Z'
        eventsResult = self.service.events().list(
            calendarId='primary', timeMin=DATE, maxResults=2500, singleEvents=True,
            orderBy='startTime').execute()
        return eventsResult

    def GenerateList(self):
        MonthDicts = defaultdict(list)
        lis = []
        for i in self.eventsResult['items']:
            try:
                _description = i['description']
            except Exception:
                _description = ''    
            try:
                _allDayDate = i['start']['date']
                _allDay = True
                _dt1 = _allDayDate
                _dt2 = _allDayDate
            except Exception:
                _dt1 = i['start']['dateTime']
                _dt2 = i['end']['dateTime']
            event = CE(
                i['id'],
                i['summary'],
                _description,
                _dt1,
                _dt2,
                True
            )

            MONTH = event.Date.month
            YEAR = event.Date.year
            MonthDicts[(YEAR,MONTH)].append(event)
        return MonthDicts

    def DeleteGoogleCalendarEvent(self,idNum):
        self.service.events().delete(calendarId='primary', eventId=idNum).execute()
        print('deleted from google calendar')

##    def AddGoogleCalendarEvent(service,event):
##        event = service.events().insert(calendarId='primary', body=event).execute()
##        print ('Event created: %s' % (event.get('htmlLink')))
        
    def AddGoogleCalendarEvent(self,event):
        event = self.service.events().insert(calendarId='primary', body=event).execute()
        print ('Event created: %s' % (event.get('htmlLink')))       


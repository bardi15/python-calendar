import datetime
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
import time
from dateutil.parser import parse
import dateutil.parser

class CalendarEvent:
    def __init__(self, idNum, summary, description,  strtTime, endTime, GoogleAccount, Date=None):
        self.idNum = idNum
        self.summary = summary
        self.description = description
        self.allday = False
        self.isValid = True
        if Date is None: #IMPORT FROM GOOGLE
            strtTime = self.dateUtilParser(strtTime)
            endTime = self.dateUtilParser(endTime)
            if strtTime == endTime:
                self.allday = True
            self.Date = strtTime.date()
            strtTime = strtTime.time()
            endTime = endTime.time()
        else:
            if type(Date) is str:
                Date = self.stringToDateTime(Date)
            if type(Date) is datetime.datetime:
                Date = Date.date()
                
            self.Date = Date

        if type(strtTime) is str or type(endTime) is str:
            strtTime = self.stringTimeToTime(strtTime)
            endTime = self.stringTimeToTime(endTime)
        elif type(strtTime) is datetime.datetime or type(endTime) is datetime.datetime:
            strtTime = strtTime.time()
            endTime = endTime.time()
            
        self.strtTime = strtTime
        self.endTime = endTime

        if  type(GoogleAccount) is not bool:
            raise ValueError('GoogleAccount Must be Boolean')
        self.GoogleAccount = GoogleAccount

        try:
            if self.strtTime > self.endTime:
                self.endTime = datetime.time(23,59,59)
        except Exception:
            self.isValid = False
        
    def __str__(self):
        return str(self.summary + ', ' + self.description)

    def dateUtilParser(self,time):
        try:
            return dateutil.parser.parse(time)
        except Exception:
            self.isValid = False
            return 0
    
    def stringToDateTime(self,string):
        try:
            SDate = string[:10]
            SDate = SDate.split('-')
            return datetime.date(int(SDate[0]),int(SDate[1]),int(SDate[2]))
        except Exception:
            self.isValid = False
            return 0

    def stringTimeToTime(self,string):
        try:
            STime = string.split(':')
            return datetime.time(int(STime[0]),int(STime[1]))
        except Exception:
            self.isValid = False
            return 0

    def endTimeToString(self):
        return(self.timeToString(self.endTime))
    
    def startTimeToString(self):
        return(self.timeToString(self.strtTime))
    
    def timeToString(self,time):
        return str(time.hour).zfill(2) + ':' + str(time.minute).zfill(2)

    def dateToString(self):
        return self.Date.strftime("%Y-%m-%d")

    def getDatabaseDate(self):
        return self.Date.strftime("%Y-%m-%d %H:%M:%S")
    
    def GetGoogleStartDate(self):
        return datetime.datetime.combine(self.Date, self.strtTime).isoformat() + 'Z'
    
    def GetGoogleEndDate(self):
        return datetime.datetime.combine(self.Date, self.endTime).isoformat() + 'Z'

    def GetYearMonthArray(self):
        return (self.Date.year, self.Date.month)


    def IsValid(self):
        return self.isValid
    
    def GetGoogleEventDictionary(self):
        if self.allday:
            event = {
              'summary': self.summary,
              'description': self.description,
              'start': {
                'dateTime': self.Date,
                'timeZone': 'Atlantic/Reykjavik',
              },
              'end': {
                'dateTime': self.Date,
                'timeZone': 'Atlantic/Reykjavik',
              'reminders': {
                'useDefault': True, },
              },
            }
            return event
        else:
            event = {
              'summary': self.summary,
              'description': self.description,
              'start': {
                'dateTime': self.GetGoogleStartDate(),
                'timeZone': 'Atlantic/Reykjavik',
              },
              'end': {
                'dateTime': self.GetGoogleEndDate(),
                'timeZone': 'Atlantic/Reykjavik',
              'reminders': {
                'useDefault': True, },
              },
            }
        return event

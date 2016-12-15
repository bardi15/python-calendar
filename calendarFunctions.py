import calendar as C
import datetime
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
import GoogleAPI as gapi

class CalendarFunc:
    def __init__(self,dBConn):
        self.currMonth = [0]
        self.today = date.today()
        self.offset = 0
        self.Gservice = gapi.GetCredentials()
        self.GoogleEvents = gapi.GenerateList(gapi.Get12MonthEvents(self.Gservice))
        self.dBConn = dBConn

    def currentMonth(self, A = None,B = None,C = None):
        if A is None and B is None and C is None:
            return self.currMonth[0]
        elif B is None and C is None:
            self.currMonth[0] += A
            return self.currMonth[0]
        elif C is None:
            raise ValueError('MISSING DAY PARAMETER')
        ##YEAR MONTH DAY
        else: pass

    def Week(self):
        l = []
        for i in range(7):
            l.append(C.day_abbr[i])
        return l
    
    def LastMonth(self,offset):
        firstdayofCurrMonth = self.today.replace(day=1)
        MonthOffset = firstdayofCurrMonth + relativedelta(months=+ offset)
        return MonthOffset

    def DateInformation(self, offset=None):
        if offset is None:
            self.offset = self.currentMonth()

        today = self.LastMonth(self.offset)
        print(today)
        month = today.month
        weekday = today.weekday()
        monthRange = C.monthrange(today.year, today.month)
        dict = {}
        dict['CurrentDay'] = datetime.datetime.today() ##NÚVERANDI DAGSETNING ÓHÁÐ OFFSET
        dict['NameOfCurrMonth'] = C.month_name[month]
        dict['DaysInMonth'] = monthRange[1]
        dict['FirstDayOfMonth'] = monthRange[0]
        dict['Year'] = today.year
        dict['DaysInWeek'] = 7
        dict['NumberOfCurrentMonth'] = month
        return dict
    
    def GoogleMonth(self,year,month):
        GE = self.GoogleEvents[year,month]
        return GE

    def AllFromGoogleMonthDay(self,gMonth,day):
        lis = []
        for i in gMonth:
            
            if i.Date.day == day:
                lis.append(i)
        return lis

    def CreateMonthDict(self,MONTH=None):
        if MONTH is None:
            MONTH = self.currentMonth()
            
        D = self.DateInformation(MONTH)
        GM = self.GoogleMonth(D['Year'],D['NumberOfCurrentMonth'])
        Location = []
        MDict = {}
        for i in range (D['DaysInMonth']):
            day = i
            starting = (day + D['FirstDayOfMonth'])
            Y = int(starting % D['DaysInWeek'])
            X = int(starting / D['DaysInWeek'])
            ThisDate = datetime.datetime(D['Year'], D['NumberOfCurrentMonth'], day+1)
            ThisDayEvents = self.dBConn.getEventObjects(ThisDate)
            ALG = self.AllFromGoogleMonthDay(GM,i+1)
            MDict[day+1] = [X,Y,ThisDate,ThisDayEvents + ALG]
        return MDict


    def AddToCalendar(self,data):
        self.dBConn.insertIntoDB(data.summary, data.description, data.getDatabaseDate(),
                                 data.startTimeToString(), data.endTimeToString(), data.allday)

    def AddToGoogleCalendar(self,data):
        event = data.GetGoogleEventDictionary()
        event = self.Gservice.events().insert(calendarId='primary', body=event).execute()
        print ('Event created: %s' % (event.get('htmlLink')))


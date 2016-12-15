import tkinter as tk
from tkinter import *
import datetime
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
import time
import calendar as C
import sqlite3
from dateutil.parser import parse
from pprint import pprint
import operator
import GoogleAPI as gapi
from CalendarEvent import CalendarEvent as CE

##GLOBAL VARIABLES
_RECTANGLESIZE = 5
_RCTHEIGHT = 50
_RCTWIDTH = 80
_APPWIDTH = 603
currMonth = [0]
newWindowSize = '400x400'
dateIs = ['']

#########################################################
##DATABASE CONNECTION                                   #
#########################################################

# breytan sem thu setur inn i returnID fallid til ad testa
t = '2016-12-16'

# insertIntoDB(summ, desc, days, stim, etim, stat)

#############################

# Tenging vid gagnagrunninn
connection = sqlite3.connect('calendarDatabase.db')
cursor = connection.cursor()

# Byr til tofluna ef hun er ekki til
def createTable():
    try:
        cursor.execute('CREATE TABLE IF NOT EXISTS cal(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, summary VARCHAR(50), description VARCHAR(300), day DATE, starttime TIME, endtime TIME, allday BOOLEAN)')
        connection.commit()
    except sqlite3.OperationalError: print('CAN NOT CREATE TABLE')

# Insertar inn i tofluna 
def insertIntoDB(summary, description, days, starttime, endtime, allday):
    cursor.execute("INSERT INTO cal(summary, description, day, starttime, endtime, allday) VALUES(?, ?, ?, ?, ?, ?)",
                   (summary, description, days, starttime, endtime, allday))
    connection.commit()
    #print('added', starttime, ' ', endtime, ' ', summary, ' ', days)

#skilar lista af ID sem er == og day parameter
def returnAllFromDay(day):
    idList = []
    result = cursor.execute('SELECT * FROM cal WHERE day = ?', (day, ))

    for row in result:
        idList.append(row)
    
    return idList

def returnAllFromID(ID):
    result = cursor.execute('SELECT * FROM cal WHERE ID = ?', (ID, ))
    p = list(cursor)
    
    return p

def returnAll():
    idList = []
    result = cursor.execute('SELECT * FROM cal', ())

    for row in result:
        idList.append(row)

    return idList

#lokar connection og cursor.
def closeConnection():
    cursor.close()
    connection.close()

#########################################################
##CALENDER FUNCTIONS                                    #
#########################################################

def currentMonth(A = None,B = None,C = None):
    if A is None and B is None and C is None:
        return currMonth[0]
    elif B is None and C is None:
        currMonth[0] += A
        return currMonth[0]
    elif C is None:
        raise ValueError('MISSING DAY PARAMETER')
    ##YEAR MONTH DAY
    else:
        print(A, B,C)
        #x = datetime.datetime(A,B,C)
        print(LastMonth(0))

def Week():
    l = []
    for i in range(7):
        l.append(C.day_abbr[i])
    return l

def LastMonth(offset):
    firstdayofCurrMonth = date.today().replace(day=1)
    MonthOffset = firstdayofCurrMonth + relativedelta(months=+ offset)
    return MonthOffset
    
def DateInformation(offset):
    today = LastMonth(offset)
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

def FromDatabaseToEventObject(ThisDate):
    #print(ThisDate)
    data = returnAllFromDay(ThisDate)
    #print(data)
    lis = []
    for i in data:
        event = CE(
            i[0], ##id
            i[1], ##summary
            i[2], ##description
            i[4], ##beginTime
            i[5], ##endTime
            False, ##from google account
            i[3] ##date
        )
        lis.append(event)
    return lis

def GoogleMonth(year,month):
    GE = GoogleEvents[year,month]
    #print('LENGTH:::::::',len(GE))
    return GE

def AllFromGoogleMonthDay(gglMonth,day):
    lis = []
    for i in gglMonth:
        
        if i.Date.day == day:
            lis.append(i)
    return lis

def CreateMonthDict(MONTH):
    D = DateInformation(MONTH)
    GM = GoogleMonth(D['Year'],D['NumberOfCurrentMonth'])
    #print('GM = GoogleMonth(D:',len(GM))
    Location = []
    MDict = {}
    for i in range (D['DaysInMonth']):
        day = i
        starting = (day + D['FirstDayOfMonth'])
        Y = int(starting % D['DaysInWeek'])
        X = int(starting / D['DaysInWeek'])
        ThisDate = datetime.datetime(D['Year'], D['NumberOfCurrentMonth'], day+1)
        ThisDayEvents = FromDatabaseToEventObject(ThisDate)
        ALG = AllFromGoogleMonthDay(GM,i+1)
        MDict[day+1] = [X,Y,ThisDate,ThisDayEvents + ALG]
    return MDict

#########################################################
##CALANDER DAYS:                                        #
#########################################################
class Calender(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.pack()
        self.Weekdays()
        self.Days()

    def CreateEvent(self, event):
        self.toplevel = Toplevel(self)
        self.toplevel.title('Events')
        self.toplevel.geometry(newWindowSize)

        self.main = Frame(self.toplevel, height=370, width=400)
        self.main.pack(side=TOP, anchor='nw')

        self.buttonFrame = Frame(self.toplevel, height=30, width=400, bg='blue')
        self.buttonFrame.pack(side=BOTTOM, expand=False)
        events = event.widget.interesting
        #print('calendar size: ', len(events))
        date = str(event.widget.dates)[0:10]
        del dateIs[:]
        dateIs.append(date)
        events = sorted(events, key=operator.attrgetter('strtTime'))
        r = 2
        if len(events) > 0:
            for i in events:
                theEvent = i.startTimeToString() +'-'+i.endTimeToString()+' - '+i.summary
                self.event = Label(self.main, text=theEvent)
                self.event.pack(anchor='nw')
                r+=2
        else:
            self.noEvent = Label(self.main, text='There are no events for this day')
            self.noEvent.pack(side=TOP)

        self.addEvent = Button(self.buttonFrame, text="Create New Event", command = lambda: Event(dateIs[0]), bd=1, relief=SOLID)
        self.addEvent.pack(side=LEFT)
        
    def Weekdays(self):
        TF = Frame(self)
        Weekdays = Week()
        TF.pack()
        for i in range(len(Weekdays)):
            box = tk.Canvas(TF, width=_RCTWIDTH, height=_RCTHEIGHT,
                            bg='white')
            box.grid(row=0,column=i)
            canvas_id = box.create_text(10, 10, anchor="nw")
            box.insert(canvas_id, 25, Weekdays[i])
            
    def Days(self):
        TX = Frame(self)
        TX.pack()
        CurrentM = DateInformation(currentMonth())
        CMonth= CreateMonthDict(currentMonth())
        #print('indays, cmonth:', len(CMonth))

        for key,value in CMonth.items():
            DAY = key
            X = value[0]
            Y = value[1]
            DATE = value[2]
            FrameColor = 'white'
            DAYEVENTS = value[3]
            if len(DAYEVENTS) > 0:
                FrameColor = 'brown'
                #print('brown')
            ##CHECKS IF ALL DAY:
            for i in DAYEVENTS:
                if i.allday:
                    #ALLDAY = True
                    FrameColor = 'blue'
                    #print('itsallday')
            if DATE.date() == datetime.datetime.today().date():
                #TODAY = True
                FrameColor = 'green'
            day = tk.Canvas(TX, width=_RCTWIDTH, height=_RCTHEIGHT, bg=FrameColor)
            day.grid(row=X, column=Y)
            text = day.create_text(10, 10, anchor="nw")
            day.interesting = DAYEVENTS
            day.dates = DATE
            day.insert(text, 25, str(DAY))
            day.bind('<Double-Button-1>', self.CreateEvent)

#########################################################
##APPLICATION FRAMEWORK                                 #
#########################################################
def currentDate():
    return str(datetime.datetime.now())[0:10]

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.parent = master
        self.initUI()
        
    def initUI(self):
        dateInfo = DateInformation(currentMonth())
        currMonth = dateInfo['NameOfCurrMonth']
        currYear = dateInfo['Year']
        dateSpec = currMonth + ' ' + str(currYear)

        self.month = Label(self.parent, text=dateSpec, font='mincho, 40')
        self.month.pack(side=TOP)

        self.d = Calender(self.parent)
        self.d.pack(pady=30)

        self.bottomFrame = Frame(self.parent, height=50, width=550, background='yellow')
        self.bottomFrame.pack(side=BOTTOM, pady=(20, 30))
        
        self.prev = Button(self.bottomFrame, text='Previous', command=self.prevMonth)
        self.prev.pack(side=LEFT)
        self.next = Button(self.bottomFrame, text='Next', command=self.nextMonth)
        self.next.pack(side=LEFT)
        cDate = currentDate()
        self.addEvent = Button(self.bottomFrame, text='Add Event', command= lambda: Event(cDate))
        self.addEvent.pack(side=LEFT)

    def prevMonth(self):
        currentMonth(-1)
        self.changeMonth()

    def nextMonth(self):
        currentMonth(1)
        self.changeMonth()

    def changeMonth(self):
        dateInfo = DateInformation(currentMonth())
        currMonth = dateInfo['NameOfCurrMonth']
        currYear = dateInfo['Year']
        dateSpec = currMonth + ' ' + str(currYear)

        self.month.destroy()
        self.month = Label(self.parent, text=dateSpec, font='mincho, 40')
        self.month.pack(side=TOP)
        self.d.destroy()
        self.d = Calender(self.parent)
        self.d.pack(pady=30)
        self.update()


#########################################################
##CREATE EVENT MODAL                                    #
#########################################################
class Event(tk.Frame):
    def __init__(self, cDate, master=None):
        super().__init__(master)
        self.currentDate = cDate
        self.pack()
        self.CreateEvent()

    def CreateEvent(self):
        #print(self.currentDate)
        self.toplevel = Toplevel()
        self.toplevel.title('Create New Event')
        self.toplevel.geometry('290x400')
        self.toplevel.resizable(0,0)

        self.topFrame = Frame(self.toplevel)
        self.topFrame.grid(row=0, column=0, sticky=W, padx=(5,0))
        self.bottomFrame = Frame(self.toplevel)
        self.bottomFrame.grid(row=1, column=0, sticky=W, padx=(5,0))

        self.EventTitle = Label(self.topFrame, text='Create Events', font="Verdana, 26")
        self.EventTitle.grid(row=0, column=0, sticky=W)

        summary = Label(self.bottomFrame, text='Title')
        summary.grid(row=1, column=0, sticky=W) 
        self.summaryEntry = Entry(self.bottomFrame, width=20)
        self.summaryEntry.grid(row=1, column=1, padx=5, pady=5, ipady=2, sticky=W)

        # d = StringVar()
        # dt = datetime.datetime.now()
        # s = dateIs[0]
        description = Label(self.bottomFrame, text='Description')
        description.grid(row=2, column=0, sticky=W+N)
        self.descriptionEntry = Text(self.bottomFrame, height=10, width=26)
        self.descriptionEntry.config(highlightcolor='#80ADDB', highlightthickness=2)
        self.descriptionEntry.config(highlightbackground='#BFBFBF', highlightthickness=0.5)
        self.descriptionEntry.grid(row=2, column=1)
        # self.descriptionEntry.insert(INSERT, str(s))

        v = StringVar()
        day = Label(self.bottomFrame, text='Date')
        day.grid(row=3, column=0, sticky=W)
        self.dayEntry = Entry(self.bottomFrame, textvariable=v)
        self.dayEntry.grid(row=3, column=1)
        v.set(self.currentDate)

        DD = datetime.datetime.now()
        w = StringVar()
        starttime = Label(self.bottomFrame, text='Starts')
        starttime.grid(row=4, column=0, sticky=W)
        self.starttimeEntry = Entry(self.bottomFrame, textvariable=w)
        self.starttimeEntry.grid(row=4, column=1)
        w.set(str(DD.hour) + ':' + str(DD.minute).zfill(2))

        D2 = DD + datetime.timedelta(hours=1)
        x = StringVar()
        enddtime = Label(self.bottomFrame, text='Ends')
        enddtime.grid(row=5, column=0, sticky=W)
        self.enddtimeEntry = Entry(self.bottomFrame, textvariable=x)
        self.enddtimeEntry.grid(row=5, column=1)
        x.set(str(D2.hour) + ':' + str(D2.minute).zfill(2))

        allday = Label(self.bottomFrame, text='All Day?')
        allday.grid(row=6, column=0, sticky=W)
        self.y = tk.IntVar()
        self.alldayEntry = tk.Checkbutton(self.bottomFrame, variable=self.y)
        self.alldayEntry.grid(row=6, column=1, sticky=W)

        dax = Label(self.bottomFrame, text='')
        dax.grid(row=7, column=0)
        
        submit = Button(self.bottomFrame, text ="Submit", command=self.on_submit)
        submit.grid(row=8, column=1, sticky=E)
##__________________________________________
        # summary = Label(self.toplevel, text='Title')
        # summary.grid(row=0, column=0)
        # self.summaryEntry = Entry(self.toplevel)
        # self.summaryEntry.grid(row=0, column=1)
        
    #     description = Label(self.toplevel, text='Description')
    #     description.grid(row=1, column=0)
    #     self.descriptionEntry = Text(self.toplevel, height=2, width=15, bd=1, relief=SOLID)
    #     self.descriptionEntry.grid(row=1, column=1)
        
    #     v = StringVar()
    #     day = Label(self.toplevel, text='Date')
    #     day.grid(row=2, column=0)
    #     self.dayEntry = Entry(self.toplevel, textvariable=v)
    #     self.dayEntry.grid(row=2, column=1)
    #     v.set(dateIs[0])


    #     DD = datetime.datetime.now()
    #     w = StringVar()
    #     starttime = Label(self.toplevel, text='Starts')
    #     starttime.grid(row=3, column=0)
    #     self.starttimeEntry = Entry(self.toplevel,textvariable=w)
    #     self.starttimeEntry.grid(row=3, column=1)
    #     w.set(str(DD.hour) + ':' + str(DD.minute))


    #     D2 = DD + datetime.timedelta(hours=1)
    #     x = StringVar()
    #     enddtime = Label(self.toplevel, text='Ends')
    #     enddtime.grid(row=4, column=0)
    #     self.enddtimeEntry = Entry(self.toplevel, textvariable=x)
    #     self.enddtimeEntry.grid(row=4, column=1)
    #     x.set(str(D2.hour) + ':' + str(D2.minute))

    #     allday = Label(self.toplevel, text='All Day?')
    #     allday.grid(row=5, column=0)
    #     self.y = tk.IntVar()
    #     self.alldayEntry = tk.Checkbutton(self.toplevel,text="", variable=self.y)
    #     self.alldayEntry.grid(row=5, column=1)

    #     dax = Label(self.toplevel, text='')
    #     dax.grid(row=6, column=1)
        
        submit = Button(self.contentFrame, text ="Submit", command=self.on_submit)
        submit.grid(row=6, column=0)
        
    def on_submit(self):
        data = GrapFromEvent(self)
        AddToCalendar(data)
        AddToGoogleCalendar(data)
        self.toplevel.destroy()
        app.changeMonth()

##def StringDateToGoogleDate(date,starts,ends):
##    SDate = date.split('-')
##    SStarts = starts.split(':')
##    SEnds = ends.split(':')
##    startDateTime = datetime.datetime(int(SDate[0]),int(SDate[1]),int(SDate[2]),int(SStarts[0]),int(SStarts[1])).isoformat() + 'Z'
##    endDateTime = datetime.datetime(int(SDate[0]),int(SDate[1]),int(SDate[2]),int(SEnds[0]),int(SEnds[1])).isoformat() + 'Z'
##    return ([startDateTime,endDateTime])

def GrapFromEvent(CreateEventData):
##    Title = CreateEventData.summaryEntry.get()
##    Description = CreateEventData.descriptionEntry.get('1.0',END)
##    Date = CreateEventData.dayEntry.get()
##    Starts = CreateEventData.starttimeEntry.get()
##    Ends = CreateEventData.enddtimeEntry.get()
##    AllDay = CreateEventData.y.get()

    event = CE(
        '00', ##id
        CreateEventData.summaryEntry.get(), ##summary
        CreateEventData.descriptionEntry.get('1.0',END), ##description
        CreateEventData.starttimeEntry.get(), ##beginTime
        CreateEventData.enddtimeEntry.get(), ##endTime
        False, ##from google account
        CreateEventData.dayEntry.get() ##date
        )

    #print(event.summary)
    #print(CreateEventData.dayEntry.get())
    return event
    #eturn ([Title,Description,Date,Starts,Ends,AllDay])

    
def AddToCalendar(data):
##    Date = data[2]
##    SDate = Date.split('-')
##    DateTimeDate = datetime.datetime(int(SDate[0]),int(SDate[1]),int(SDate[2]))
    insertIntoDB(data.summary, data.description, data.getDatabaseDate(), data.startTimeToString(), data.endTimeToString(), data.allday)

def AddToGoogleCalendar(data):
    event = data.GetGoogleEventDictionary()
##    #G = Gservice
##    dateDate = StringDateToGoogleDate(data[2],data[3],data[4])
##    event = {
##      'summary': data[0],
##      'description': data[1],
##      'start': {
##        'dateTime': dateDate[0],
##        'timeZone': 'Atlantic/Reykjavik',
##      },
##      'end': {
##        'dateTime': dateDate[1],
##        'timeZone': 'Atlantic/Reykjavik',
##      'reminders': {
##        'useDefault': True, },
##      },
##    }
    event = Gservice.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))

##VIEW SINGLE DAY ON CALENDAR
#-----##TODO##


##VIEW ALL EVENTS FOR MONTH ON CALENDAR
#-----##TODO##


##CONNECT CALENDAR TO GOOGLE CALENDAR
#-----##TODO##




#########################################################
##START                                                 #
#########################################################

##TEST DATA FOR SQL
createTable()
##
##x = datetime.datetime(2016,11,13)
###print(x)
##insertIntoDB('HI', 'THAR', x, '14:00', '18:00', 'False')
##
x = datetime.datetime(2016,12,29)
insertIntoDB('HI', 'THAR', x, '14:00', '18:00', 'False')
##
##x = datetime.datetime(2016,12,17)
##insertIntoDB('BYE', 'THAR', x, '14:00', '18:00', 'False')
###currentMonth(0,1,2)
Gservice = gapi.GetCredentials()
GoogleEvents = gapi.GenerateList(gapi.Get12MonthEvents(Gservice))
root = tk.Tk()
root.title('QCal')
app = Application(root)
app.parent.geometry('603x570')
app.parent.resizable(0,0)
app.mainloop()
closeConnection()



import tkinter as tk
from tkinter import *
import datetime
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
import time
import calendar as C
import sqlite3
from dateutil.parser import parse
import GoogleAPI

##GLOBAL VARIABLES
_RECTANGLESIZE = 5
_RCTHEIGHT = 50
_RCTWIDTH = 80
_APPWIDTH = 603
currMonth = [-1]

#########################################################
##DATABASE CONNECTION                                   #
#########################################################


########  Test data  ########
##summ = 'Boliti'
##desc = 'alltaf i boltanum'
##days = '2016-12-18'
##stim = '12:00'
##etim = '10:00'
##stat = True

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
##BUTTON FUNCTIONS:                                     #
#########################################################

def prevMonth():
    print(currentMonth(-1))

def nextMonth():
    print(currentMonth(1))


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
    #print(offset)
    firstdayofCurrMonth = date.today().replace(day=1)
    MonthOffset = firstdayofCurrMonth + relativedelta(months=+ offset)
    return MonthOffset
    
def DateInformation(offset):
    #print(offset)
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

def GoogleMonth(year,month):
    #print(year,month)
    return GoogleAPI.GetEvents(year,month)

def AllFromGoogleMonthDay(gglMonth,day):
    lis = []
    for i in gglMonth:
        Stime = i['starttime']
        if Stime.day == day:
            Date = Stime.date()
            TY = Stime.hour
            TZ = Stime.minute
            #strtTime = datetime.time(TY, TZ)
            strtTime = str(TY).zfill(2) + ':' + str(TZ).zfill(2)
            Etime = i['endtime']
            UY = Etime.hour
            UZ = Etime.minute
            #endTime = datetime.time(UY,UZ)
            endTime = str(UY).zfill(2) + ':' + str(UZ).zfill(2)
            summary = i['summary']
            description = i['description']
            allday = i['allday']
            lis.append(['GLG',summary, description, Date, strtTime, endTime, allday])
    return lis

def SuperList(SQLLIST,GLGLIST):
    megalist = []
    for i in SQLLIST:
        TIMED = datetime.datetime.strptime(i[3], '%Y-%m-%d %H:%M:%S').date()
        k = [i[0],i[1],i[2],TIMED,i[4],i[5],i[6]]
        #print(k)
        megalist.append(k)
    for y in GLGLIST:
        #dTime = datetime.combine(y[3], datetime.min.time())
        g = [y[0],y[1],y[2],y[3],y[4],y[5],y[6]]
        #print(g)
        megalist.append(g)

    megalist.sort(key=lambda item:item[4], reverse=True)
    return megalist

def CreateMonthDict(MONTH):
    D = DateInformation(MONTH)
    GM = GoogleMonth(D['Year'],D['NumberOfCurrentMonth'])
    
    Location = []
    MDict = {}
    for i in range (D['DaysInMonth']):
        day = i
        #AllFromGoogleMonthDay(GM,i+1)
        starting = (day + D['FirstDayOfMonth'])
        Y = int(starting % D['DaysInWeek'])
        X = int(starting / D['DaysInWeek'])
        ThisDate = datetime.datetime(D['Year'], D['NumberOfCurrentMonth'], day+1)
        ThisDayEvents = returnAllFromDay(ThisDate)
        ALG = AllFromGoogleMonthDay(GM,i+1)
        superList = SuperList(ThisDayEvents, ALG)
####        for i in range(len(superList)):
####            print(str(i) , '  : ', superList[i])
##        #print(superList)
##        if (len(ThisDayEvents) > 99 and len(ALG) > 0):
##            print('ThisDayEvents\n')
##            print(ThisDayEvents)
##            print('\n\nAllFromGoogleMonthDay')
##            print(AllFromGoogleMonthDay(GM,i+1))
        MDict[day+1] = [X,Y,ThisDate,superList]
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
        
    def Weekdays(self):
        TF = Frame(master=None)
        Weekdays = Week()
        TF.pack()
        for i in range(len(Weekdays)):
            box = tk.Canvas(TF, width=_RCTWIDTH, height=_RCTHEIGHT,
                            bg='white')
            box.grid(row=0,column=i)
            canvas_id = box.create_text(10, 10, anchor="nw")
            box.insert(canvas_id, 25, Weekdays[i])
            
    def Days(self):
        TX = Frame(master=None)
        TX.pack()
        CurrentM = DateInformation(currentMonth())
        CMonth= CreateMonthDict(currentMonth())

        for key,value in CMonth.items():
            DAY = key
            X = value[0]
            Y = value[1]
            DATE = value[2]
            DAYEVENTS = value[3]
            ALLDAY = False

            ##CHECKS IF ALL DAY:
            for i in DAYEVENTS:
                if i[6] == 1:
                    ALLDAY = True

            if ALLDAY:
                day = tk.Canvas(TX, width=_RCTWIDTH, height=_RCTHEIGHT,
                                bg='blue')                
            elif len(DAYEVENTS) > 0:
                day = tk.Canvas(TX, width=_RCTWIDTH, height=_RCTHEIGHT,
                                bg='brown')
            else:
                day = tk.Canvas(TX, width=_RCTWIDTH, height=_RCTHEIGHT,
                                bg='white') 
            day.grid(row=X, column=Y)
            text = day.create_text(10, 10, anchor="nw")
            day.insert(text, 25, str(DAY))


#########################################################
##APPLICATION FRAMEWORK                                 #
#########################################################
class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.parent = master
        self.initUI()
        
    def initUI(self):
        currMonth = DateInformation(currentMonth())
        curr = currMonth['NameOfCurrMonth']

        ##TOP FRAME
        self.top = Frame(self.parent, bg='',width=603, height=50)
        self.top.pack(fill='both',expand=True)
        CurrentMonth = Label(self.top, text=curr)
        CurrentMonth.pack(side=LEFT)
        CurrentMonth.config(font=("mincho", 40))

        self.middle = Frame(self.parent,bg='green', width=603, height=200)
        self.middle.pack(expand=False)

        ##MIDDLE FRAME
        d = Calender(self.middle)
        d.pack()

        ##BOTTOM FRAME        
        self.bottom = Frame(self.parent, bg='', width=603, height=50)
        self.bottom.pack(expand=False)
        self.prev = Button(self.bottom, text='Previous', command=prevMonth)
        self.prev.pack(side=LEFT, padx=5, pady=5)
        self.next = Button(self.bottom, text='Next', command=nextMonth)
        self.next.pack(side=RIGHT,padx=5, pady=5)
        
        self.nextx = Button(self.bottom, text='Add Event', command=Event)
        self.nextx.pack(side=RIGHT,padx=5, pady=5)


#########################################################
##CREATE EVENT MODAL                                    #
#########################################################
class Event(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.pack()
        self.CreateEvent()

    def CreateEvent(self):
        self.toplevel = Toplevel()
        summary = Label(self.toplevel, text='Title')
        summary.grid(row=0, column=0)
        self.summaryEntry = Entry(self.toplevel)
        self.summaryEntry.grid(row=0, column=1)
        
        description = Label(self.toplevel, text='Description')
        description.grid(row=1, column=0)
        self.descriptionEntry = Text(self.toplevel, height=2, width=15)
        self.descriptionEntry.grid(row=1, column=1)

        v = StringVar()
        day = Label(self.toplevel, text='Date')
        day.grid(row=2, column=0)
        self.dayEntry = Entry(self.toplevel, textvariable=v)
        self.dayEntry.grid(row=2, column=1)
        v.set(str(date.today()))

        DD = datetime.datetime.now()
        w = StringVar()
        starttime = Label(self.toplevel, text='Starts')
        starttime.grid(row=3, column=0)
        self.starttimeEntry = Entry(self.toplevel,textvariable=w)
        self.starttimeEntry.grid(row=3, column=1)
        w.set(str(DD.hour) + ':' + str(DD.minute))


        D2 = DD + datetime.timedelta(hours=1)
        x = StringVar()
        enddtime = Label(self.toplevel, text='Ends')
        enddtime.grid(row=4, column=0)
        self.enddtimeEntry = Entry(self.toplevel, textvariable=x)
        self.enddtimeEntry.grid(row=4, column=1)
        x.set(str(D2.hour) + ':' + str(D2.minute))

        allday = Label(self.toplevel, text='All Day?')
        allday.grid(row=5, column=0)
        self.y = tk.IntVar()
        self.alldayEntry = tk.Checkbutton(self.toplevel,text="", variable=self.y)
        self.alldayEntry.grid(row=5, column=1)

        dax = Label(self.toplevel, text='')
        dax.grid(row=6, column=1)
        
        submit = Button(self.toplevel, text ="Submit", command=self.on_submit)
        submit.grid(row=6, column=0)
        
    def on_submit(self):
        AddToCalendar(self)
        self.toplevel.destroy()


def AddToCalendar(CreateEventData):
    Title = CreateEventData.summaryEntry.get()
    Description = CreateEventData.descriptionEntry.get('1.0',END)
    
    Date = CreateEventData.dayEntry.get()
    SDate = Date.split('-')
    DateTimeDate = datetime.datetime(int(SDate[0]),int(SDate[1]),int(SDate[2]))

    Starts = CreateEventData.starttimeEntry.get()
    Ends = CreateEventData.enddtimeEntry.get()
    AllDay = CreateEventData.y.get()
    insertIntoDB(Title, Description, DateTimeDate, Starts, Ends, AllDay)
    print(Title,Description,Date,Starts,Ends,DateTimeDate,AllDay)

##VIEW SINGLE DAY ON CALENDAR
#-----##TODO##


##VIEW ALL EVENTS FOR MONTH ON CALENDAR
#-----##TODO##


##CONNECT CALENDAR TO GOOGLE CALENDAR
#-----##TODO##




#########################################################
##START                                                 #
#########################################################
# root = tk.Tk()
# app = Application(master=root)
# app.mainloop()


##TEST DATA FOR SQL
createTable()

x = datetime.datetime(2016,11,13)
#print(x)
#insertIntoDB('HI', 'THAR', x, '14:00', '18:00', 'False')

x = datetime.datetime(2016,12,13)
#insertIntoDB('HI', 'THAR', x, '14:00', '18:00', 'False')

x = datetime.datetime(2016,12,17)
#insertIntoDB('BYE', 'THAR', x, '14:00', '18:00', 'False')
#currentMonth(0,1,2)

root = tk.Tk()
app = Application(root)
app.parent.geometry('603x450')
app.parent.resizable(0,0)
app.mainloop()
closeConnection()



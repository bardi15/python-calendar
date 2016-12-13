import tkinter as tk
from tkinter import *
import datetime
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
import calendar as C
import sqlite3

##GLOBAL VARIABLES
_RECTANGLESIZE = 5
_RCTHEIGHT = 50
_RCTWIDTH = 80
_CURRENTMONTH = 0

#########################################################
##DATABASE CONNECTION                                   #
#########################################################


########  Test data  ########
summ = 'Boliti'
desc = 'alltaf i boltanum'
days = '2016-12-18'
stim = '12:00'
etim = '10:00'
stat = True

# breytan sem thu setur inn i returnID fallid til ad testa
t = '2016-12-18'

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
    except sqlite3.OperationalError:

# Insertar inn i tofluna 
def insertIntoDB(summary, description, days, starttime, endtime, allday):
    cursor.execute("INSERT INTO cal(summary, description, day, starttime, endtime, allday) VALUES(?, ?, ?, ?, ?, ?)", (summary, description, days, starttime, endtime, allday))
    connection.commit()

#skilar lista af ID sem er == og day parameter
def returnID(day):
    idList = []
    result = cursor.execute('SELECT ID FROM cal WHERE day = ?', (day, ))

    for row in result:
        idList.append(row[0])
    
    return idList

#lokar connection og cursor.
def closeConnection():
    cursor.close()
    connection.close()


#########################################################
##BUTTON FUNCTIONS:                                     #
#########################################################

def prevMonth():
    _CURRENTMONTH -= 1
    print(_CURRENTMONTH)

def nextMonth():
    _CURRENTMONTH += 1
    print(_CURRENTMONTH)

#########################################################
##CALENDER FUNCTIONS                                    #
#########################################################

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
    print(dict)
    return dict

def CreateMonthDict(MONTH):
    D = DateInformation(MONTH)
    Location = []
    MDict = {}
    print(D['DaysInMonth'])
    for i in range (D['DaysInMonth']):
        day = i
        starting = (day + D['FirstDayOfMonth'])
        Y = int(starting % D['DaysInWeek'])
        X = int(starting / D['DaysInWeek'])
        MDict[day+1] = [X,Y]
    return MDict

#########################################################
##GUI CLASS:                                            #
#########################################################
class Calender(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.pack()
        # self.Month()
        self.Weekdays()
        self.Days()
        
        #self.CreateEvent(4)
    # def Month(self):
    #     TM = Frame(master=None)
    #     TM.pack()
    #     CurrMonth = DateInformation(_CURRENTMONTH)['NameOfCurrMonth']
    #     mon = tk.Canvas(TM, width=_RCTWIDTH*7, height=_RCTHEIGHT)
    #     mon.grid(row=0,column=0)
    #     text = mon.create_text(10, 10, anchor="nw")
    #     mon.insert(text,25,CurrMonth)
        
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
        CMonth= CreateMonthDict(_CURRENTMONTH)

        for key,value in CMonth.items():
            DAY = key
            X = value[0]
            Y = value[1]
            day = tk.Canvas(TX, width=_RCTWIDTH, height=_RCTHEIGHT,
                            bg='white')
            day.grid(row=X, column=Y)
            text = day.create_text(10, 10, anchor="nw")
            day.insert(text, 25, str(DAY))

    def CreateEvent(self,date):
        toplevel = Toplevel()
        summary = Label(toplevel, text='Title')
        summary.grid(row=0, column=0)
        summaryEntry = Entry(toplevel)
        summaryEntry.grid(row=0, column=1)
        
        description = Label(toplevel, text='Description')
        description.grid(row=1, column=0)
        description = Entry(toplevel)
        description.grid(row=1, column=1)

        day = Label(toplevel, text='Date')
        day.grid(row=2, column=0)
        day = Entry(toplevel)
        day.grid(row=2, column=1)

        starttime = Label(toplevel, text='Starts')
        starttime.grid(row=3, column=0)
        starttime = Entry(toplevel)
        starttime.grid(row=3, column=1)

        enddtime = Label(toplevel, text='Ends')
        enddtime.grid(row=4, column=0)
        enddtime = Entry(toplevel)
        enddtime.grid(row=4, column=1)

        allday = Label(toplevel, text='All Day?')
        allday.grid(row=5, column=0)
        allday = Entry(toplevel)
        allday.grid(row=5, column=1)

        p = 'hallo'
        
        dax = Label(toplevel, text=str(date))
        dax.grid(row=6, column=1)
        submit = Button(toplevel, text ="Submit", command=self.on_submit(p))
        submit.grid(row=6, column=0)
        
    def on_submit(self,p):
        print(p)

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.parent = master
        self.initUI()
        
    def initUI(self):
        currMonth = DateInformation(_CURRENTMONTH)
        curr = currMonth['NameOfCurrMonth']
        self.top = Frame(self.parent, bg='',width=603, height=50)
        self.top.pack(fill='both',expand=True)
        CurrentMonth = Label(self.top, text=curr)
        CurrentMonth.pack(side=LEFT)
        CurrentMonth.config(font=("mincho", 40))

        self.middle = Frame(self.parent,bg='green', width=603, height=200)
        self.middle.pack(expand=False)
        d = Calender(self.middle)
        d.pack()
        self.bottom = Frame(self.parent, bg='', width=603, height=50)
        self.bottom.pack(expand=False)
        self.prev = Button(self.bottom, text='Previous', command=prevMonth)
        self.prev.pack(side=LEFT, padx=5, pady=5)
        self.next = Button(self.bottom, text='Next', command=nextMonth)
        self.next.pack(side=RIGHT,padx=5, pady=5)




        







##ADD EVENTS TO CALENDAR
#-----##TODO##


##REMOVE EVENTS FROM CALENDAR
#-----##TODO##


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
root = tk.Tk()
app = Application(root)

app.parent.geometry('603x450')
app.parent.resizable(0,0)
app.mainloop()
closeConnection()



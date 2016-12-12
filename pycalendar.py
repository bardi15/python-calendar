import tkinter as tk
from tkinter import *
import datetime
import calendar as C

##GLOBAL VARIABLES
_RECTANGLESIZE = 5
_RCTHEIGHT = 50
_RCTWIDTH = 80


##DATABASE CONNECTION
#-----##TODO##


##CALENDER FUNCTIONS

def Week():
    l = []
    for i in range(7):
        l.append(C.day_name[i])
    return l

def DateInformation():
    today = datetime.datetime.today()
    month = today.month
    weekday = today.weekday()
    monthRange = C.monthrange(today.year, today.month)
    dict = {}
    dict['DayOfMonth'] = today.day
    dict['NameOfCurrDay'] = C.day_name[weekday]
    dict['NameOfCurrMonth'] = C.month_name[month]
    dict['DaysInMonth'] = monthRange[1]
    dict['FirstDayOfMonth'] = monthRange[0]
    dict['DaysInWeek'] = 7
    return dict

def CreateMonthDict():
    D = DateInformation()
    Location = []
    MDict = {}
    for i in range (D['DaysInMonth']):
        day = i
        starting = (day + D['FirstDayOfMonth'])
        Y = int(starting % D['DaysInWeek'])
        X = int(starting / D['DaysInWeek'])
        MDict[day+1] = [X,Y]
    return MDict


##GUI CLASS:

class Application(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.pack()
        self.Weekdays()
        self.Days()
        #self.CreateEvent()

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
        CMonth= CreateMonthDict()

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

        dax = Label(toplevel, text=str(date))
        dax.grid(row=6, column=1)

        







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





##START

root = tk.Tk()
app = Application(master=root)
app.mainloop()


            


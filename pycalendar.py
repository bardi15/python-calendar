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


            


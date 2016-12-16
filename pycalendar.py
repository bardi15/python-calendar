import tkinter as tk
from tkinter import *
import datetime
import operator

from calendarEvent import CalendarEvent as CE
from database import Database
from calendarFunctions import CalendarFunc

##GLOBAL VARIABLES
_RECTANGLESIZE = 5
_RCTHEIGHT = 50
_RCTWIDTH = 80
_APPWIDTH = 603

newWindowSize = '400x400'
dateIs = ['']

#########################################################
##CALANDER DAYS:                                        #
#########################################################
class Calender(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.pack()
        self.Weekdays()
        self.Days()

    def DisplayEvents(self, event):
        self.toplevel = Toplevel(self)
        self.toplevel.title('Events')
        self.toplevel.geometry(newWindowSize)

        self.main = Frame(self.toplevel, height=370, width=400)
        self.main.pack(side=TOP, anchor='nw')

        self.buttonFrame = Frame(self.toplevel, height=30, width=400, bg='blue')
        self.buttonFrame.pack(side=BOTTOM, expand=False)

        self.events = event.widget.interesting
        date = str(event.widget.dates)[0:10]
        del dateIs[:]
        dateIs.append(date)
        self.events = sorted(self.events, key=operator.attrgetter('strtTime'))
        #r = 2
        if len(self.events) > 0:
            for i in range(len(self.events)):
                self.line = Frame(self.main,height=30, width=400)
                self.line.pack(expand=True, anchor='nw')
                theEvent = (self.events[i].startTimeToString() +'-'+
                            self.events[i].endTimeToString()+' - '+
                            self.events[i].summary)
                self.event = Label(self.line, text=theEvent)
                self.event.pack(side=LEFT, expand=True)
                self.remove = Button(self.line, text="Remove", command =lambda i=i: self.Delete(i), bd=1, relief=SOLID )
                self.remove.pack(side=RIGHT,expand=True)
                #r+=2
        else:
            self.noEvent = Label(self.main, text='There are no events for this day')
            self.noEvent.pack(side=TOP)
        self.addEvent = Button(self.buttonFrame, text="Create New Event", command = lambda: Event(dateIs[0]), bd=1, relief=SOLID)
        self.addEvent.pack(side=LEFT)

    def Delete(self,i):
        event = self.events[i]
        CFUtil.DeleteFromCalendar(event.idNum,event.GoogleAccount)
        CFUtil.RefreshMonth(event, True)
        self.toplevel.destroy()
        app.changeMonth()
        
    def Weekdays(self):
        TF = Frame(self)
        Weekdays = CFUtil.Week()
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
        CurrentM = CFUtil.DateInformation()
        CMonth= CFUtil.CreateMonthDict()
        for key,value in CMonth.items():
            DAY = key
            X = value[0]
            Y = value[1]
            DATE = value[2]
            FrameColor = 'white'
            DAYEVENTS = value[3]
            if len(DAYEVENTS) > 0:
                FrameColor = 'brown'
            ##CHECKS IF ALL DAY:
            for i in DAYEVENTS:
                if i.allday:
                    #ALLDAY = True
                    FrameColor = 'blue'
            if DATE.date() == datetime.datetime.today().date():
                #TODAY = True
                FrameColor = 'green'
            day = tk.Canvas(TX, width=_RCTWIDTH, height=_RCTHEIGHT, bg=FrameColor)
            day.grid(row=X, column=Y)
            text = day.create_text(10, 10, anchor="nw")
            day.interesting = DAYEVENTS
            day.dates = DATE
            day.insert(text, 25, str(DAY))
            day.bind('<Double-Button-1>', self.DisplayEvents)

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
        dateInfo = CFUtil.DateInformation()
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

        self.cur = Button(self.bottomFrame, text = 'Current Month', command = self.currMonth)
        self.cur.pack(side = LEFT)


    def currMonth(self):
        today = datetime.datetime.today()
        CFUtil.currentMonth(today.year, today.month, today.day)
        self.changeMonth()

    def prevMonth(self):
        CFUtil.currentMonth(-1)
        self.changeMonth()

    def nextMonth(self):
        CFUtil.currentMonth(1)
        self.changeMonth()

    def changeMonth(self):
        dateInfo = CFUtil.DateInformation()
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

        description = Label(self.bottomFrame, text='Description')
        description.grid(row=2, column=0, sticky=W+N)
        self.descriptionEntry = Text(self.bottomFrame, height=10, width=26)
        self.descriptionEntry.config(highlightcolor='#80ADDB', highlightthickness=2)
        self.descriptionEntry.config(highlightbackground='#BFBFBF', highlightthickness=0.5)
        self.descriptionEntry.grid(row=2, column=1)
        
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

        googleButton = Label(self.bottomFrame, text='Add to Google?')
        googleButton.grid(row=7, column=0, sticky=W)
        self.g = tk.IntVar()
        self.googleButton = tk.Checkbutton(self.bottomFrame, variable=self.g, onvalue = 1, offvalue = 0)
        self.googleButton.grid(row=7, column=1, sticky=W)

        dax = Label(self.bottomFrame, text='')
        dax.grid(row=8, column=0)
        
        submit = Button(self.bottomFrame, text ="Submit", command=self.on_submit)
        submit.grid(row=9, column=1, sticky=E)
        
    def on_submit(self):
        data = GrapFromEvent(self)

########ÚTFÆRA:
        if not data.IsValid():
            sys.exit()
##############
            
        if self.g.get() == 1:
            CFUtil.AddToGoogleCalendar(data)
        else:
            CFUtil.AddToCalendar(data)
        self.toplevel.destroy()
        CFUtil.RefreshMonth(data,False)
        app.changeMonth()


def GrapFromEvent(CreateEventData):
    event = CE(
        None, ##id
        CreateEventData.summaryEntry.get(), ##summary
        CreateEventData.descriptionEntry.get('1.0',END), ##description
        CreateEventData.starttimeEntry.get(), ##beginTime
        CreateEventData.enddtimeEntry.get(), ##endTime
        False, ##from google account
        CreateEventData.dayEntry.get() ##date
        )
    return event

#########################################################
##START                                                 #
#########################################################

dBConn = Database()
dBConn.createTable()

CFUtil = CalendarFunc(dBConn)

root = tk.Tk()
root.title('QCal')
app = Application(root)
app.parent.geometry('603x570')
app.parent.resizable(0,0)
app.mainloop()

dBConn.closeConnection()

import sqlite3
from calendarEvent import CalendarEvent as CE

#########################################################
##DATABASE CONNECTION                                   #
#########################################################
class Database:
    def __init__(self):
        self.connection = sqlite3.connect('calendarDatabase.db')
        self.cursor = self.connection.cursor()
        
    # Byr til tofluna ef hun er ekki til
    def createTable(self):
        try:
            self.cursor.execute('CREATE TABLE IF NOT EXISTS cal(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, summary VARCHAR(50), description VARCHAR(300), day DATE, starttime TIME, endtime TIME, allday BOOLEAN)')
            self.connection.commit()
        except sqlite3.OperationalError: print('CAN NOT CREATE TABLE')

    # Insertar inn i tofluna 
    def insertIntoDB(self, summary, description, days, starttime, endtime, allday):
        self.cursor.execute("INSERT INTO cal(summary, description, day, starttime, endtime, allday) VALUES(?, ?, ?, ?, ?, ?)",
                       (summary, description, days, starttime, endtime, allday))
        self.connection.commit()

    #skilar lista af ID sem er == og day parameter
    def returnAllFromDay(self, day):
        idList = []
        result = self.cursor.execute('SELECT * FROM cal WHERE day = ?', (day, ))

        for row in result:
            idList.append(row)
        
        return idList

    def returnAllFromID(self,ID):
        result = self.cursor.execute('SELECT * FROM cal WHERE ID = ?', (ID, ))
        p = list(self.cursor)
        
        return p

    def returnAll(self):
        idList = []
        result = self.cursor.execute('SELECT * FROM cal', ())

        for row in result:
            idList.append(row)

        return idList
    
    def removeRow(self,idNum):
        result = self.cursor.execute("DELETE FROM cal WHERE ID=?", (idNum,))
        self.connection.commit()
    def getEventObjects(self, ThisDate):
        data = self.returnAllFromDay(ThisDate)
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

    #lokar connection og cursor.
    def closeConnection(self):
        self.cursor.close()
        self.connection.close()

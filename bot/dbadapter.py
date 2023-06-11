import sqlite3
from datetime import date
from datetime import datetime

class dbAdapter:
    
    __db = sqlite3.connect('server.db')
    __sql = __db.cursor()
    __sql.execute("""
    CREATE TABLE IF NOT EXISTS UserData(
        user_id     INTEGER PRIMARY KEY,
        user_name   TEXT,
        days_in_row INTEGER,
        last_event  TEXT,
        last_date   TEXT
    );
    """)
    __sql.execute("""
    CREATE TABLE IF NOT EXISTS  UserStatistics(
        user_id       INTEGER REFERENCES UserData (user_id),
        event_name    TEXT,
        times_partied INTEGER
    );           
    """)
    
     
    def dbCommit(self):
        self.__db.commit()
    
     
    def insertNewUser(self, userId: int, userName: str):
        self.__sql.execute(f"SELECT user_id FROM UserData WHERE user_id = {userId}")
        if self.__sql.fetchone() is None:
            self.__sql.execute(f"INSERT INTO UserData(user_id,user_name,days_in_row) VALUES({userId}, '{userName}', 0)")
            self.__db.commit()
    
     
    def userExists(self, userId: int):
        self.__sql.execute(f"SELECT user_id FROM UserData WHERE user_id = {userId}")
        if self.__sql.fetchone() is None:
            return False
        else:
            return True
        
     
    def incrementDaysInRow(self, userId: int):
        self.__sql.execute(f"UPDATE UserData SET days_in_row=days_in_row+1 WHERE user_id = {userId}")
        self.__db.commit()
    
     
    def resetDaysInRow(self, userId: int):
        self.__sql.execute(f"UPDATE UserData SET days_in_row=1 WHERE user_id = {userId}")
        self.__db.commit()
        
     
    def getDaysInRow(self, userId: int):
        self.__sql.execute(f"SELECT days_in_row FROM UserData WHERE user_id = {userId}")
        row = self.__sql.fetchone()
        self.__db.commit()
        if row is None:
            self.incrementDaysInRow(self, userId)
            self.__db.commit()
            return 1
        else:
            return row[0]
           
     
    def updateLastEvent(self, userId: int, eventName: str):
        self.__sql.execute(f"UPDATE UserData SET last_event='{eventName}' WHERE user_id = {userId}")
        self.__db.commit()
        self.__sql.execute(f"SELECT user_id FROM UserStatistics WHERE user_id = {userId} AND event_name ='{eventName}'")
        row = self.__sql.fetchone()
        if row is None:
            self.__sql.execute(f"INSERT INTO UserStatistics(user_id, event_name, times_partied) VALUES({userId}, '{eventName}', 1)")
            self.__db.commit()
        else:
            self.__sql.execute(f"UPDATE UserStatistics SET times_partied=times_partied+1 WHERE user_id = {userId} AND event_name ='{eventName}'")  
            self.__db.commit()
        
    
    def updateLastDate(self, userId: int, date: datetime):
        self.__sql.execute(f"UPDATE UserData SET last_date='{date}' WHERE user_id = {userId}")
        self.__db.commit()
    
    
    def getLastDate(self, userId) -> datetime:
        self.__sql.execute(f"SELECT last_date FROM UserData WHERE user_id = {userId}")
        row = self.__sql.fetchone()
        self.__db.commit()
        if row[0] is None:
            return datetime(year = 1, month = 1, day = 1, hour = 1, minute = 1, second = 1)
        else:
            return datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        
    def totalTimesPartied(self, userId) -> int:
        self.__sql.execute(f"SELECT SUM(times_partied) FROM UserStatistics WHERE user_id = user_id")
        row = self.__sql.fetch()
        if row is None:
            return 0
        else:
            return row[0]
    

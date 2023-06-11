import requests
import datetime
import re
from bs4 import BeautifulSoup

class CalendFetcher:
    
    __urlBase = "https://www.calend.ru/"
    __urlEvent = ""
    __eventId = ""
    __eventName = ""
    __eventImageLink = ""
    
    @classmethod
    def getCurrentEventName(cls, currentDate: datetime) -> str:
        url = cls.__urlBase + "/day/" + str(currentDate.year) + "-" + str(currentDate.month) + "-" + str(currentDate.day)
        try:
            soup = BeautifulSoup(requests.get(url).text, features='lxml')
            linkToEvent = soup.find("p", {"class":"descr descrFixed"}).find('a').attrs['href']
            cls.__eventId = re.search('https://www.calend.ru/holidays/0/0/(.*)/', linkToEvent).group(1)
            cls.__urlEvent = cls.__urlBase + "holidays/0/0/" + cls.__eventId
            cls.__eventName = soup.find("a", {"href":f"{linkToEvent}"}).find('img').attrs['alt']
            soup = BeautifulSoup(requests.get(cls.__urlEvent).text, features='lxml')
            cls.__eventImageLink = soup.find("p", {"class":"float"}).find('img').attrs['src']
        except:
            cls.__eventId = ""
            cls.__urlEvent = ""
            cls.__eventName = ""
            cls.__eventImageLink = ""
            
        return cls.__eventName
    
    @classmethod
    def getCurrentEventExtraText(cls) -> str:
        soup = BeautifulSoup(requests.get(cls.__urlEvent).text, features='lxml')
        try:
            eventExtratextRaw = soup.find("div", {"class":"maintext"}).text
            eventExtratext = eventExtratextRaw[0:4040] + '' + cls.__urlEvent
        except:
            eventExtratext = "nothing"
        return eventExtratext

    @classmethod
    def getCurrentEventExtraImage(cls) -> str:            
        return cls.__eventImageLink
    
    
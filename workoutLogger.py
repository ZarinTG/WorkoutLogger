import tkinter as tk
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow as run_oauth2
from oauth2client.file import Storage as CredentialStorage
import httplib2
from apiclient.discovery import build as discovery_build
from tkinter.constants import *
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt

TITLE_FONT = ("Helvetica", 18, "bold")

class WorkoutLogger(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, TotalDistance, InputWorkout, PrintDateDistance, PlotChart):
            pageName = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[pageName] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        #print(self.frames)
        self.show_frame("StartPage")

    def show_frame(self, pageName):
        '''Show a frame for the given page name'''
        frame = self.frames[pageName]
        #frame.getdata()
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        welcomeText = "Welcome to workout logger! It is {0} today"
        welcomeText = welcomeText.format(datetime.datetime.fromtimestamp(time.time()).strftime("%d/%m/%Y"))
        label = tk.Label(self, text=welcomeText, font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        choice = tk.IntVar()
        radioButtonDistance=tk.Radiobutton(self, text="Get Total Distance Covered", variable=choice, value=1,
                                           command=lambda: controller.show_frame("TotalDistance"))
        radioButtonInput=tk.Radiobutton(self, text="Input Workout", variable=choice, value=2,
                                        command=lambda: controller.show_frame("InputWorkout"))
        radioButtonPrint=tk.Radiobutton(self, text="Print Date Distance", variable=choice, value=3,
                                                    command=lambda: controller.show_frame("PrintDateDistance"))
        radioButtonChart=tk.Radiobutton(self, text="Plot Chart", variable=choice, value=4,
                                                    command=lambda: controller.show_frame("PlotChart"))
        
        radioButtonDistance.pack()
        radioButtonInput.pack()
        radioButtonPrint.pack()
        radioButtonChart.pack()

class TotalDistance(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        distance = self.getTotalDistanceCovered()
        distanceDisplayText = str("Total Distance Covered is :")
        distList = []
        for entry in distance:
            distList.append(str(entry))
            distList.append(str(distance[entry]))
        labelText = tk.Label(self, text=distanceDisplayText, font=TITLE_FONT)
        labelText.pack(side="top", fill="x", pady=10)
        labelDist = tk.Label(self, text=' '.join(distList), font=TITLE_FONT)
        labelDist.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

    def getTotalDistanceCovered(self):
        result = service.spreadsheets().values().get(spreadsheetId='1jSh5iNMI9azaaprs5BulcJXtGLiotMLPIRvjloUtTqI', range='Sheet1!A:C', majorDimension='ROWS').execute()
        #print(result)
        #distance = 'distance'
        #timestamp = 'timestamp'
        monthPersonDistMap = dict()
        personMap = dict()
        for row in result.get('values'):
            #print(row)
            #log = dict()
            #log[distance]=row[1]
            #month=datetime.datetime.fromtimestamp(row[0]).timetuple()
            #personDistMap=monthPersonDistMap.get(month)
            #if personDistMap is None:
                #personDistMap = dict()
            #monthPersonDistMap[month]=personDistMap
            
            personSplit=row[2].split(',')
            for person in personSplit:
                if personMap.get(person) is None:
                    #No entry for this person, add one
                    personMap[person] = float(row[1])
                else:
                    personMap[person] = float(personMap.get(person)) + float(row[1])
            #print('Total distance covered by each person')
            #print(personMap)
        return personMap

class InputWorkout(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Input a Workout", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        labelDistance = tk.Label(self, text="Enter Distance")
        distText = str()
        distanceEntry = tk.Entry(self, textvariable=distText)
        labelPerson = tk.Label(self, text="Enter Person")
        personText = str()
        personEntry = tk.Entry(self, textvariable=personText)
        labelDate = tk.Label(self, text="Enter Date in DD/MM/YYYY format")
        dateText = str()
        dateEntry = tk.Entry(self, textvariable=dateText)
        labelDistance.pack()
        distanceEntry.pack(after=labelDistance)
        labelPerson.pack()
        personEntry.pack(after=labelPerson)

        labelDate.pack()
        dateEntry.pack(after=labelDate)
        saveButton = tk.Button(self, text="Save", command=lambda: self.saveData(distanceEntry.get(),personEntry.get(), dateEntry.get()))
        saveButton.pack()
        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))
        button.pack()

    def saveData(self, distance, person, d):
        #distance = float(distanceEntry.get())
        #print(dist)
        #person = personEntry.get()
        #print(p)
        #d = dateEntry.get()
        #print(d)
        timestamp = 0
        if len(d)==0:
                timestamp = int(round(time.time() * 1000))
        else:
                timestamp = datetime.datetime.strptime(d, "%d/%m/%Y").timestamp()*1000
        #print(millis)
        #reconvert to string to check...
        #print(datetime.datetime.fromtimestamp(millis).strftime("%d/%m/%Y"))
        #def writeToSheet(timestamp, distance, person):
        #cellValues = [ [timestamp,distance,person], ['1482543000000','100','Z'] ]
        cellValues = [ [timestamp,distance,person] ]
        body=dict()
        body['values']=cellValues
        result = service.spreadsheets().values().append(spreadsheetId='1jSh5iNMI9azaaprs5BulcJXtGLiotMLPIRvjloUtTqI', range='Sheet1!A:C',valueInputOption='RAW', body=body).execute()
        #print(result)
        
class PrintDateDistance(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Prints person's distance by date", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        personDateDistanceMap = self.getPersonDateAndDistance()
        
        for person in sorted(personDateDistanceMap.keys()):
            #print(type(person))
            text = "Dates and Distance for {0} is "
            distanceDisplayText=text.format(person)
            labelText = tk.Label(self, text=distanceDisplayText, font=TITLE_FONT)
            labelText.pack(side="top", fill="x", pady=10)
            dateDistanceMap = personDateDistanceMap.get(person)
            listDateDist=[]
            for date in sorted(dateDistanceMap.keys()):
                dateDist = "Date {0}, Distance {1}"
                dateInt = int(date)/1000
                dateStr = datetime.datetime.fromtimestamp(dateInt).strftime("%d/%m/%Y")
                dateDistDisplay=dateDist.format(dateStr,dateDistanceMap.get(date))
                listDateDist.append(dateDistDisplay)
                #labelDate = tk.Label(self, text=dateDistDisplay, font=TITLE_FONT)
                #labelDist = tk.Label(self, text=str(dateDistanceMap[date]), font=TITLE_FONT)
                #labelDist.pack(side="top", fill="x", pady=10)
            textWidget = tk.Text(self)
            #textWidget.delete(tk.END)
            textWidget.insert(tk.END, ','.join(listDateDist))
            textWidget.configure(state=tk.DISABLED)
            textWidget.pack()
        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))
        button.pack()

    def getPersonDateAndDistance(self):
        result = service.spreadsheets().values().get(spreadsheetId='1jSh5iNMI9azaaprs5BulcJXtGLiotMLPIRvjloUtTqI', range='Sheet1!A:C', majorDimension='ROWS').execute()
        personDateDistMap = dict()
        for entry in result.get('values'):
            p = str(entry[2])
            personSplit=p.split(',')
            date = entry[0]
            dist = float(entry[1])
            for person in personSplit:
                if personDateDistMap.get(person) is None:
                    dateDistMap = dict()
                    dateDistMap[date]=dist
                    personDateDistMap[person]=dateDistMap
                else:
                    dateDistMap = personDateDistMap.get(person)
                    if dateDistMap.get(date) is None:
                        dateDistMap[date]=dist
                    else:
                        dateDistMap[date]=float(dateDistMap.get(date)) + dist
        return personDateDistMap

class PlotChart(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Plots a stacked bar by date", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        personDateListDistanceMap = self.getPersonDateListDistanceMap()
        print(personDateListDistanceMap)
        dateList = self.getDateList()
        personList=[]
        for person in personDateListDistanceMap.keys():
            personList.append(person)
            for date in dateList:
                listWorkouts = personDateListDistanceMap.get(person).get(date)
                #if listWorkouts is None or len(lisWorkouts)==0:
                    

        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))
        button.pack()

    def getDateList(self):
        dateList=[]
        #Return a list of dates from 24th december 2016 till current date
        start = datetime.date(year=2016, month=12, day=24)
        timestruct=time.localtime()
        end = datetime.date(year=timestruct.tm_year, month=timestruct.tm_mon, day=timestruct.tm_mday)
        for n in range((end-start).days):
            dateList.append(start+datetime.timedelta(n))
        return dateList

    def getPersonDateListDistanceMap(self):
        result = service.spreadsheets().values().get(spreadsheetId='1jSh5iNMI9azaaprs5BulcJXtGLiotMLPIRvjloUtTqI', range='Sheet1!A:C', majorDimension='ROWS').execute()

        personDateListDistanceMap = dict()
        for entry in result.get('values'):
            p = str(entry[2])
            personSplit=p.split(',')
            date = datetime.date.fromtimestamp(int(entry[0])/1000)
            dist = float(entry[1])
            for person in personSplit:
                if personDateListDistanceMap.get(person) is None:
                    dateDistListMap = dict()
                    dateDistListMap[date]=[dist]
                    personDateListDistanceMap[person]=dateDistListMap
                else:
                    dateDistListMap = personDateListDistanceMap.get(person)
                    if dateDistListMap.get(date) is None:
                        dateDistListMap[date]=[dist]
                    else:
                        dateDistListMap.get(date).append(dist)
        return personDateListDistanceMap

   
if __name__ == "__main__":
    flow = flow_from_clientsecrets('C:\\Users\\zarinr\\Desktop\\client_id.json',scope='https://www.googleapis.com/auth/spreadsheets', redirect_uri='http://www.google.com')
    flow.step1_get_authorize_url()
    credential_storage = CredentialStorage('C:\\Users\\zarinr\\Desktop\\credentials.json')
    credentials = credential_storage.get()
    #credentials = run_oauth2(flow, credential_storage)
    credentials.authorize(httplib2.Http())
    #response = http.request('https://sheets.googleapis.com/v4/spreadsheets/1jSh5iNMI9azaaprs5BulcJXtGLiotMLPIRvjloUtTqI?includeGridData=true',method='GET')
    service = discovery_build('sheets','v4', credentials=credentials)
    app = WorkoutLogger()
    app.mainloop()

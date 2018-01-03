import tkinter as tk
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow as run_oauth2
from oauth2client.file import Storage as CredentialStorage
import httplib2
import apiclient.discovery
import time
import datetime
import bar_chart as chart

TITLE_FONT = ("Helvetica", 18, "bold")

flow = flow_from_clientsecrets('C:\\Users\\zarinr\\Desktop\\client_id.json',
                               scope='https://www.googleapis.com/auth/spreadsheets',
                               redirect_uri='http://www.google.com')
flow.step1_get_authorize_url()
credential_storage = CredentialStorage('C:\\Users\\zarinr\\Desktop\\credentials.json')
credentials = credential_storage.get()
# credentials = run_oauth2(flow, credential_storage)
credentials.authorize(httplib2.Http())

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
        yearPersonDistance = self.getTotalDistanceCovered()
        distanceDisplayText = str("Total Distance Covered is :")
        distList = []
        for key, value in yearPersonDistance.items():
            distList.append(str(key))
            for key1, value1 in value.items():
                distList.append(str(key1))
                distList.append(str(value1))
        labelText = tk.Label(self, text=distanceDisplayText, font=TITLE_FONT)
        labelText.pack(side="top", fill="x", pady=10)
        labelDist = tk.Label(self, text=' '.join(distList), font=TITLE_FONT)
        labelDist.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

    def getTotalDistanceCovered(self):
        service = apiclient.discovery.build('sheets', 'v4', credentials=credentials)
        result = service.spreadsheets().values().get(spreadsheetId='1jSh5iNMI9azaaprs5BulcJXtGLiotMLPIRvjloUtTqI', range='Sheet1!A:C', majorDimension='ROWS').execute()
        yearPersonDistMap = dict()

        for row in result.get('values'):
            workoutDate = int(row[0])/1000
            year=datetime.datetime.fromtimestamp(int(row[0])/1000).year
            personMap = dict()
            if yearPersonDistMap.get(year) is None:
                yearPersonDistMap[year] = personMap
            else:
                personMap = yearPersonDistMap[year]

            personSplit=row[2].split(',')
            for person in personSplit:
                if personMap.get(person) is None:
                    #No entry for this person, add one
                    personMap[person] = float(row[1])
                else:
                    personMap[person] = float(personMap.get(person)) + float(row[1])
        return yearPersonDistMap

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
        timestamp = 0
        if len(d)==0:
                timestamp = int(round(time.time() * 1000))
        else:
                timestamp = datetime.datetime.strptime(d, "%d/%m/%Y").timestamp()*1000
        cellValues = [ [timestamp,distance,person] ]
        body=dict()
        body['values']=cellValues
        service = apiclient.discovery.build('sheets', 'v4', credentials=credentials)
        result = service.spreadsheets().values().append(spreadsheetId='1jSh5iNMI9azaaprs5BulcJXtGLiotMLPIRvjloUtTqI', range='Sheet1!A:C',valueInputOption='RAW', body=body).execute()

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
        service = apiclient.discovery.build('sheets', 'v4', credentials=credentials)
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

        personMonthAndDistance = self.getPersonMonthAndDistance()
        monthYearList = self.getMonthYearList()
        personList = []
        personDistListMap = dict()
        for person in personMonthAndDistance.keys():
            personList.append(person)
            dist_list = []
            personDistListMap[person] = dist_list

            for monthYear in monthYearList:
                distance = personMonthAndDistance.get(person).get(monthYear)
                dist_list.append(distance)

        #chart.draw_chart('Month', 'Distance(km)', 'Person Distance Chart', monthYearList, personList, personDistListMap)

        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("StartPage"))
        button.pack()

    def getMonthYearList(self):
        monthYearList = []
        #Return a list of month-years from 24th december 2016 till current date
        start = datetime.date(year=2016, month=12, day=24)
        timestruct=time.localtime()
        end = datetime.date(year=timestruct.tm_year, month=timestruct.tm_mon, day=timestruct.tm_mday)
        for n in range((end-start).days):
            date=start+datetime.timedelta(n)
            monthYearList.append(str(date.month)+"-"+str(date.year))
        return monthYearList

    # def getDateList(self):
    #     dateList=[]
    #     #Return a list of dates from 24th december 2016 till current date
    #     start = datetime.date(year=2016, month=12, day=24)
    #     timestruct=time.localtime()
    #     end = datetime.date(year=timestruct.tm_year, month=timestruct.tm_mon, day=timestruct.tm_mday)
    #     for n in range((end-start).days):
    #         dateList.append(start+datetime.timedelta(n))
    #     return dateList

    # def getPersonDateListDistanceMap(self):
    #     result = service.spreadsheets().values().get(spreadsheetId='1jSh5iNMI9azaaprs5BulcJXtGLiotMLPIRvjloUtTqI', range='Sheet1!A:C', majorDimension='ROWS').execute()
    #
    #     personDateListDistanceMap = dict()
    #     for entry in result.get('values'):
    #         p = str(entry[2])
    #         personSplit=p.split(',')
    #         date = datetime.date.fromtimestamp(int(entry[0])/1000)
    #         dist = float(entry[1])
    #         for person in personSplit:
    #             if personDateListDistanceMap.get(person) is None:
    #                 dateDistListMap = dict()
    #                 dateDistListMap[date]=[dist]
    #                 personDateListDistanceMap[person]=dateDistListMap
    #             else:
    #                 dateDistListMap = personDateListDistanceMap.get(person)
    #                 if dateDistListMap.get(date) is None:
    #                     dateDistListMap[date]=[dist]
    #                 else:
    #                     dateDistListMap.get(date).append(dist)
    #     return personDateListDistanceMap

    def getPersonMonthAndDistance(self):
        service = apiclient.discovery.build('sheets', 'v4', credentials=credentials)
        result = service.spreadsheets().values().get(spreadsheetId='1jSh5iNMI9azaaprs5BulcJXtGLiotMLPIRvjloUtTqI', range='Sheet1!A:C', majorDimension='ROWS').execute()
        personMonthDistMap = dict()
        for entry in result.get('values'):
            p = str(entry[2])
            personSplit=p.split(',')
            date = datetime.date.fromtimestamp(int(entry[0])/1000)
            #Extract month from date-time value
            month_year_list=[str(date.month), str(date.year)]
            month_year = "-".join(month_year_list)
            dist = float(entry[1])
            for person in personSplit:
                if personMonthDistMap.get(person) is None:
                    monthDistMap = dict()
                    monthDistMap[month_year]=dist
                    personMonthDistMap[person]=monthDistMap
                else:
                    monthDistMap = personMonthDistMap.get(person)
                    if monthDistMap.get(month_year) is None:
                        monthDistMap[month_year]=dist
                    else:
                        monthDistMap[month_year]=float(monthDistMap.get(month_year)) + dist
        return personMonthDistMap

   
if __name__ == "__main__":
    app = WorkoutLogger()
    app.mainloop()

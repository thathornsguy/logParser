import os
import tkFileDialog

def getDirectory():
    logDirectory = ""
    if os.path.isfile(".\cfg"):
        configFile = open(".\cfg", "r")
        logDirectory = configFile.readline().strip()
        configFile.close()
    else:
        logDirectory = tkFileDialog.askdirectory()
        if logDirectory == "":
            return ""
        configFile = open(".\cfg", "w")
        configFile.write(logDirectory)
        configFile.close()
    return logDirectory

class logManager:
    def __init__(self):
        # dictionary of all log objects
        self.logDictionary = {}
        self.logList = []
        self.lastLinesStats = {}
        self.lastLineStats = {}
        self.fails = 0
        self.nonFails = 0
        self.directory = getDirectory()
        self.populate()


    def empty(self):
        self.logDictionary = {}
        self.logList = []
        self.lastLinesStats = {}
        self.lastLineStats = {}
        self.fails = 0
        self.nonFails = 0

    def insertLog(self,log):
        # insert the log into the dictionary indexed by the date time the log was created (ie the filename)
        self.logDictionary[(log.date,log.time)] = log
        self.logList.append(log)

    def getLog(self,date,time):
        return self.logDictionary[(date,time)]

    def update(self):
        logDirectory = tkFileDialog.askdirectory()
        if logDirectory == "":
            return 1
        self.empty()
        self.directory = logDirectory
        os.remove("cfg")
        configFile = open(".\cfg", "w")
        configFile.write(logDirectory)
        configFile.close()
        self.populate()
        return 0


    def populate(self):
        allLogNames = os.listdir(self.directory)
        # iterate over all the log files and create a log object associated with that file
        for logFileName in allLogNames:
            # create log object
            entry = log(5)
            # populate the object with the data from the log file
            entry.populate(self.directory, logFileName)
            # add the log to the list of logs
            self.insertLog(entry)
        self.globalStats()

    def globalStats(self):
        for log in self.logList:
            if log.cleanExit == True:
                self.nonFails += 1
            else:
                self.fails += 1
            if len(log.lastEntries) != 0:
                lastLine = log.lastEntries[-1]
                if lastLine[0] == ":":
                    key = lastLine.split(" ")[0]
                    if key in self.lastLineStats:
                        self.lastLineStats[key].append(lastLine)
                    else:
                        self.lastLineStats[key] = [lastLine]
                else:
                    if "Failed Assertion" in self.lastLineStats:
                        self.lastLineStats["Failed Assertion"].append(lastLine)
                    else:
                        self.lastLineStats["Failed Assertion"]=[lastLine]

            for line in log.lastEntries:
                if line[0] == ":":
                    key = line.split(" ")[0]
                    if key in self.lastLinesStats:
                        self.lastLinesStats[key].append(line)
                    else:
                        self.lastLinesStats[key] = [line]
                else:
                    if "Failed Assertion" in self.lastLinesStats:
                        self.lastLinesStats["Failed Assertion"].append(line)
                    else:
                        self.lastLinesStats["Failed Assertion"] = [line]

    def getStats(self):
        toReturn = "Number of Logs: "+str(len(self.logList))+"\n"
        toReturn += "Number of Clean Exits: " + str(self.nonFails) + "\n"
        toReturn += "Number of Failures: "+str(self.fails)+"\n"
        toReturn += "Tag Occurrence Count for the last line: \n"
        for key,lines in self.lastLineStats.items():
            toReturn += "\tTag: "+key+"\n"
            toReturn += "\tCount: "+str(len(lines))+"\n\n"

        toReturn += "Tag Occurrence Count for the last "+str(self.logList[0].maxCapacity)+" lines: \n"
        for key,lines in self.lastLinesStats.items():
            toReturn += "\tTag: "+key+"\n"
            toReturn += "\tCount: "+str(len(lines))+"\n\n"
        return toReturn

class log:
    def __init__(self, capacity):
        # list containing the initial information of the log file
        self.launchInfo = launchInfo()
        # contains all the lines of a log file
        self.entryList = []
        # contains the last n log entries, where n is equal to maxCapacity
        self.lastEntries = []
        # determines the maximum number of logs to keep in lastEntries
        self.maxCapacity = capacity
        # dictionary of lists indexed by the tags at the beginning of an entry ie ":tag:"
        self.countDictionary = {}
        # filename of the log file the associated with this data
        self.fileName = ""
        # the directory where the log file is found
        self.directory = ""
        # date time the log file was created, taken from the filename
        self.date = ""
        self.time = ""
        # true if the launcher made it past the launch info
        self.launched = True
        # true if play session associated with the log did closed gracefully
        self.cleanExit = False
        # the statistics object associated with this log file
        self.stats = None

    def cleanDateTime(self,rawDate):
        splitTimeDate = rawDate.split("_")
        date = splitTimeDate[0].split("-")[1]
        time = splitTimeDate[1].split(".")[0]
        self.date = date[0:2] + "/" + date[2:4]+"/"+date[4:6]
        self.time = time[0:2] + ":" + time[2:4]+":"+time[4:6]


    # populates the log object with values
    def populate(self, directory, fileName):
        # open the logs file descriptor
        logFile = open(directory+"\\"+fileName)
        # set directory and filename
        self.directory = directory
        self.fileName = fileName
        # take the filename and create a date and time format
        self.cleanDateTime(fileName)
        # createdLaunchInfo is set to true when the launch info of the log File has been read in and created
        createdLaunchInfo = False
        # iterate over all lines in the log file
        for logLine in logFile:
            # strip off the new line at the end of each line
            cleanedLine = logLine.strip()
            # determine if the line is part of the launch info or the data entries
            if cleanedLine.startswith(":") and not createdLaunchInfo:
                # if the line is a data entry and the launch info has not been created
                # populate the launch info for this log object
                self.launchInfo.populate(self.entryList, fileName)
                # clean out the entry list of launch info
                self.entryList = []
                # set the createdLaunchInfo to start adding data entries to the entry list
                createdLaunchInfo = True
            #     add a line from the log file to the entryList
            self.entryList.append(cleanedLine)
        # check if there was no data and only launch info
        if not self.launchInfo.dataAdded:
            self.launchInfo.populate(self.entryList, fileName)
            self.entryList = []
            self.launched = False
        # get the last n entries in the list of all data
        self.lastEntries = self.entryList[(self.maxCapacity * -1):]
        # check to see if the game closed gracefully for this log
        self.checkExit()
        # gereate statistics for this log
        self.stats = logStatistics(self)
        # close the log file descriptor
        logFile.close()

    def checkExit(self):
        if self.launched:
            if ":display: Closing wglGraphicsWindow" in  self.lastEntries:
                self.cleanExit = True


    def allLogsToString(self):
        toReturn = ""
        lineNum = len(self.launchInfo.allLines) + 1
        for line in self.entryList:
            toReturn += str(lineNum) +": "+ line + "\n"
            lineNum += 1
        return toReturn


    def logSummaryToString(self):
        toReturn = ""
        toReturn += "Log Filename: "+self.fileName+"\n"
        toReturn += "Date: " + self.date + "\n"
        toReturn += "Time: " + self.time + "\n"
        toReturn += "Clean Exit: " + str(self.cleanExit) + "\n"
        toReturn += "Launched Correctly: " + str(self.launched) + "\n"
        toReturn += self.launchInfo.getValues() + "\n"
        toReturn += "Last " + str(self.maxCapacity) + " Line(s): \n"
        for line in self.lastEntries:
            toReturn += "\t" + line + "\n"
        return toReturn

# stores the launch info of a log file
class launchInfo:
    def __init__(self):
        # the filename associated with the launch info
        self.fileName = ""
        # all lines that are deemed part of the launch info
        self.allLines = []
        # the server attempting to be connected to
        self.gameServer = ""
        # the cookie associated with the log file
        self.cookie = ""
        # the language being used
        self.language = ""
        # the graphics info for the current play session, ie driver information
        self.graphicsInfo = []
        # version of TLOPO that is associated with the log file
        self.version = ""
        # lines from the launch information that has not been given a specific value name within this class
        self.unsorted = []
        # is true if there is launch information missing that is normally inside a log file
        self.incomplete = True
        # bool to check if populate has been run
        self.dataAdded = False

    # populate a launchInfo object
    def populate(self, lines,fileName):
        # report that data has been added
        self.dataAdded = True
        # store all the launchinfo into all lines
        self.allLines = lines
        # the filename of the log file
        self.fileName = fileName
        # iterate over all lines of the launch info
        for line in lines:
            # fill known launch info variables within this class otherwise store in unsorted
            if "TLOPO_GAMESERVER" in line:
                self.gameServer = line.split("=")[-1].strip()
            elif "TLOPO_PLAYCOOKIE" in line:
                self.cookie = line.split("=")[-1].strip()
            elif "Running in language:" in line:
                self.language = line.split(":")[-1].strip()
            elif "getDriver" in line:
                self.graphicsInfo.append(line.split(":")[-1].strip())
            elif "serverVersion:" in line:
                self.version = line.split(":")[-1].strip()
            else:
                self.unsorted.append(line)
        # check to see if all expected information has been found in the launch info
        self.checkCompleteness()

    # sets the incomplete value to false if all expected information is found during the populate function
    def checkCompleteness(self):
        # giant logical statement that determines if all fields have been found
        if self.allLines != [] and self.gameServer != "" and self.cookie != "" and self.language != "" and self.graphicsInfo != [] and self.version != "" and self.unsorted != []:
            self.incomplete = False

    # functions that helps with debugging
    def printValues(self):
        print("\tLog Filename: "+self.fileName)
        print("\tGame Server: "+self.gameServer)
        print("\tCookie: "+self.cookie)
        print("\tLanguage: "+self.language)
        print("\tGraphics Info: "+str(self.graphicsInfo))
        print("\tVersion: "+self.version)
        print("\tUnsorted: "+str(self.unsorted))
        print("\tMissing Info: "+str(self.incomplete))

    # returns all information associated with this object to be printed in the textbox of the main window
    def getValues(self):
        toReturn = \
        "Game Server: "+self.gameServer+ \
        "\nCookie: "+self.cookie+ \
        "\nLanguage: "+self.language+ \
        "\nGraphics Info: "
        for line in self.graphicsInfo:
            toReturn += "\n\t"+ line
        toReturn+="\nVersion: "+self.version
        toReturn += "\nMissing Launch Info: "+str(self.incomplete)
        return toReturn


    # concatenate every line of the launch info and return it
    def getAll(self):
        toReturn = ""
        lineNum = 1
        for line in self.allLines:
            toReturn += str(lineNum) +": "+line + "\n"
            lineNum += 1
        return toReturn

class logStatistics:

    def __init__(self,log):
        self.numLines =  len(log.entryList) + len(log.launchInfo.allLines)
        self.numLaunchLines = len(log.launchInfo.allLines)
        self.numDataLines = len(log.entryList)
        self.dataLineDictionary = {}
        lineNum = len(log.launchInfo.allLines) + 1
        for line in log.entryList:
            if line[0] == ":":
                key = line.split(" ")[0]
                if key in self.dataLineDictionary:
                    self.dataLineDictionary[key].append(str(lineNum))
                else:
                    self.dataLineDictionary[key] = [str(lineNum)]
            else:
                if "Failed Assertion" in self.dataLineDictionary:
                    self.dataLineDictionary["Failed Assertion"].append(str(lineNum))
                else:
                    self.dataLineDictionary["Failed Assertion"] = [str(lineNum)]
            lineNum += 1

    def toString(self):
        toReturn = "Number of Lines Total: " + str(self.numLines)+"\n"
        toReturn += "Number of Launch Lines: " + str(self.numLaunchLines)+"\n"
        toReturn += "Number of Data Lines: "+ str(self.numDataLines) + "\n"
        if self.numDataLines != 0:
            toReturn += "Instances of Each Tag: \n"
            for key,lineNums in  self.dataLineDictionary.items():
                    toReturn += "\tLine Tag: \""+key+"\"\n"
                    toReturn += "\tCount: "+str(len(lineNums))+"\n"
                    toReturn += "\tLine Numbers: " + str(lineNums)+"\n\n"





        return toReturn

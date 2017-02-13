import os
import tkFileDialog

# used to get a log directory on startup, might be merged with other version of this method
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

# contains all the logs being looked at
class logManager:
    def __init__(self):
        # dictionary of all log objects
        self.logDictionary = {}
        # list of all log objects
        self.logList = []
        # contains the information needed to produce the statistics for the last 5 lines
        self.lastLinesStats = {}
        # contains the information needed the produce the statistics for the last line
        self.lastLineStats = {}
        # the number of logs that did not close gracefully
        self.fails = 0
        # the number of logs that closed gracefully
        self.nonFails = 0
        # the directory of the log files being looked at
        self.directory = getDirectory()
        # if a directory was not chosen, close the program
        if self.directory == "":
            exit(-1)
        # get the data from the directory chosen
        self.populate()

    # empty the values of the class, used injuction with update
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
        # append the log to the logList
        self.logList.append(log)

    # return the log specified by the given date and time
    def getLog(self,date,time):
        return self.logDictionary[(date,time)]

    # update the information of this object based on the new directory provided
    def update(self):
        # ask user for a new directory
        logDirectory = tkFileDialog.askdirectory()
        # if no directory was chosen, do nothing
        if logDirectory == "":
            return 1
        # update the directory being looked at
        self.directory = logDirectory
        # remove the current configuration file
        os.remove("cfg")
        # create a new configuration file storing the new directory
        configFile = open(".\cfg", "w")
        configFile.write(logDirectory)
        configFile.close()
        self.refresh()
        return 0

    # delete and update all log objects inside the current directory
    def refresh(self):
        # empty all data
        self.empty()
        # call populate to update this object's data
        self.populate()

    # method used to initially fill this object with data
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

    # create the global statistics based on the current data
    def globalStats(self):
        # iterate over all logs that are stored in logList
        for log in self.logList:
            # count the number of fails and non fails
            if log.cleanExit == True:
                self.nonFails += 1
            else:
                self.fails += 1
            # check to see if lastEntries is populated, ie generated non launch info
            # if it has add that last entry to the lastLineStats dictionary
            if len(log.lastEntries) != 0:
                # get the last line of the last 5 lines
                lastLine = log.lastEntries[-1]
                # check to see if the line is a tag or not
                if lastLine[0] == ":":
                    # if it is a tag extract what tag it is
                    key = lastLine.split(" ")[0]
                    # check to see if this tag has laready been entered into the dictionary
                    if key in self.lastLineStats:
                        self.lastLineStats[key].append(lastLine)
                    else:
                        # if it hasn't create a list containing the line and add it to the dictionary
                        self.lastLineStats[key] = [lastLine]
                else:
                    # check to see if a Failed assertion has been added or not
                    if "Assertion Failed" in self.lastLineStats:
                        self.lastLineStats["Assertion Failed"].append(lastLine)
                    else:
                        self.lastLineStats["Assertion Failed"]=[lastLine]

            # iterate over all lines in lastEntries, virtually the same thing as above as far as comments are concerned
            for line in log.lastEntries:
                if line[0] == ":":
                    key = line.split(" ")[0]
                    if key in self.lastLinesStats:
                        self.lastLinesStats[key].append(line)
                    else:
                        self.lastLinesStats[key] = [line]
                else:
                    if "Assertion Failed" in self.lastLinesStats:
                        self.lastLinesStats["Assertion Failed"].append(line)
                    else:
                        self.lastLinesStats["Assertion Failed"] = [line]

    # produce a string consisting of the global stats information, relatively self explanatory
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

    # get the date and time from the filename of this logfile
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

    # determine if this log file exited gracefully or not and set the cleanExit variable
    def checkExit(self):
        # first check if this log has more than launch information
        if self.launched:
            # then check if the following line happens to be in the last 5 entries
            if ":display: Closing wglGraphicsWindow" in  self.lastEntries:
                self.cleanExit = True

    # concatenates all lines of data and their associated line numbers into a string separated by newlines
    def allLogsToString(self):
        toReturn = ""
        lineNum = len(self.launchInfo.allLines) + 1
        for line in self.entryList:
            toReturn += str(lineNum) +": "+ line + "\n"
            lineNum += 1
        return toReturn

    # generate the summary page information and return it as a string
    def logSummaryToString(self):
        toReturn = "Log Filename: "+self.fileName+"\n"
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

# class that represents the statistics for a log object
class logStatistics:

    def __init__(self,log):
        # the number of lines in the log file
        self.numLines =  len(log.entryList) + len(log.launchInfo.allLines)
        # the number of lines associated with the launch information
        self.numLaunchLines = len(log.launchInfo.allLines)
        # the number of lines associated with data
        self.numDataLines = len(log.entryList)
        # the dictionary containing all data tags keys and their line numbers
        self.dataLineDictionary = {}
        # get the inital line number based on the last number of the launch info
        lineNum = len(log.launchInfo.allLines) + 1
        # iterate over all lines in the log object
        for line in log.entryList:
            # check to see if the line has a tag
            if line[0] == ":":
                # extract the tag from the line
                key = line.split(" ")[0]
                # insert the line number of this line indexed by the tag
                if key in self.dataLineDictionary:
                    self.dataLineDictionary[key].append(str(lineNum))
                else:
                    self.dataLineDictionary[key] = [str(lineNum)]
            else:
                # insert the line number of this line indexed by assertion failed
                if "Assertion Failed" in self.dataLineDictionary:
                    self.dataLineDictionary["Assertion Failed"].append(str(lineNum))
                else:
                    self.dataLineDictionary["Assertion Failed"] = [str(lineNum)]
            lineNum += 1

    # generate a string representation of this object, used on the summary page
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

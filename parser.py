import os
from windowClasses import *
from datastorage import *
import tkFileDialog
from Tkinter import *

Tk().withdraw()
# logDirectory is the path name pointing to the directory with the log files
if os.path.isfile(".\cfg"):
    configFile = open(".\cfg","r")
    logDirectory = configFile.readline().strip()
    configFile.close()
else:
    logDirectory = tkFileDialog.askdirectory()
    configFile = open(".\cfg","w")
    configFile.write(logDirectory)
    configFile.close()
# allLogNames contains the fileNames of every log file within logDirectory
allLogNames = os.listdir(logDirectory)
# allLogs contains all instances of the log class created from the log files, that is then stored in a logManager object
allLogs = logManager()
# iterate over all the log files and create a log object associated with that file
for logFileName in allLogNames:
    # create log object
    entry = log(5)
    # populate the object with the data from the log file
    entry.populate(logDirectory,logFileName)
    # add the log to the list of logs
    allLogs.insertLog(entry)
allLogs.globalStats()
test = bootWindow(allLogs)


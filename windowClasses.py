from Tkinter import *


class bootWindow:
    def __init__(self,allEntries):
        # index of the currently selected log
        self.logIndex = -1
        # the logManager object associated with the found log files
        self.allEntries = allEntries
        # the number representing the current tab
        self.tabNum = 0
        # the root of the Tkinter window
        self.root = Tk()
        # the height of the window being created, creating a class variable in case I want to make the window dynamic insize
        self.height = int(self.root.winfo_screenheight()/1.5)
        # the width of the window being created, creating a class variable in case I want to make the window dynamic insize
        self.width = int(self.root.winfo_screenwidth()/1.5)
        # setting the height and width of the tkinter window
        self.root.geometry(str(self.width) + "x" + str(self.height))
        # prevent the window from being resized, may change later to allow dynamic window sizes
        self.root.resizable(0,0)
        # the frame containing the listbox for log files as well as the textbox for the data associated with log files
        mainFrame = Frame(self.root)
        # the frame containing the listbox for log files and the scroll bar for the listbox
        listBoxFrame = Frame(mainFrame)
        # the frame that puts space in between the listbox and textbox
        mainSpacer = Frame(mainFrame,width=20)

        # the grame containing the details textbox and the x and y scroll bars for that textbox
        detailFrame = Frame(mainFrame)
        # the detail tabs frame
        buttonTabFrame = Frame(detailFrame)
        buttonSpacer = Frame(buttonTabFrame, width=int(self.width/3))
        # scrollbar for the log listbox
        yLogScroll = Scrollbar(listBoxFrame)
        # scrollbars for the detail textbox
        xDetailScroll = Scrollbar(detailFrame,orient=HORIZONTAL)
        yDetailScroll = Scrollbar(detailFrame)


        # the listbox containing all logfile entries
        self.logListBox = Listbox(listBoxFrame, height=int(self.height//17), width = int(self.width//30),yscrollcommand=yLogScroll.set)
        self.logListBox.pack(side="left")
        # the textbox that is filled with information about a log file when it is selected in the listbox on the left side of the window
        self.detailText = Text(detailFrame,wrap=NONE, height=int(self.height//18), width = int(self.width//10.6),xscrollcommand=xDetailScroll.set,yscrollcommand=yDetailScroll.set)
        # button that changes the detail textbox to the summary info fo the log file
        self.summaryButton = Button(buttonTabFrame,command = self.summaryButtonCommand, text="Log Summary",bg="#d3d3d3")
        self.launchInfoButton = Button(buttonTabFrame,command = self.launchInfoButtonCommand, text="Launch Info",bg="#d3d3d3")
        self.contentsButton = Button(buttonTabFrame,command = self.contentsButtonCommand, text="Log Contents",bg="#d3d3d3")
        self.logStatsButton = Button(buttonTabFrame,command = self.logStatsButtonCommand, text="Log Stats",bg="#d3d3d3")
        self.globalStatsButton = Button(buttonTabFrame,command = self.globalStatsButtonCommand, text="Global Stats",bg="#d3d3d3")
        # add the buttons to the window
        buttonSpacer.pack(side="right")
        self.summaryButton.pack(side="left")
        self.launchInfoButton.pack(side="left")
        self.contentsButton.pack(side="left")
        self.logStatsButton.pack(side="left")
        self.globalStatsButton.pack(side="left")
        # add the button frame to the window
        buttonTabFrame.pack(side="top",pady=2)
        # load the scroll bars into their respective frames
        xDetailScroll.pack(side = "bottom",fill=X)
        yDetailScroll.pack(side = "right",fill=Y)
        yLogScroll.pack(side = "right",fill=Y)

        # load the  textbox into the main page
        self.detailText.pack(side = "left")

        # configurations to make the scroll bars work
        yDetailScroll.config(command=self.detailText.yview)
        xDetailScroll.config(command=self.detailText.xview)
        yLogScroll.config(command = self.logListBox.yview)

        # load the frames into the main window
        listBoxFrame.pack(side="left")

        detailFrame.pack(side="right")
        mainSpacer.pack()
        mainFrame.pack(side = "top")
        # create the menu for the window
        m = Menu(self.root)
        m.add_command(label="File")
        # add the menu to the main window
        self.root.config(menu=m)
        # add all the log files found in the specified directory to the listbox
        self.addToLogFileList(allEntries)
        # the logic that changes the textbox to the contents of the selected log file
        self.logListBox.bind('<<ListboxSelect>>', self.updateTextBox)
        # override what happens after the x button is hit to close the window
        self.root.protocol('WM_DELETE_WINDOW',exit)
        # causes the window to open
        self.root.mainloop()

    # when a log is selected from the listbox update the textbox to the contents of the associated log
    def updateTextBox(self,evt):
        # some code below taken from stack overflow
        # get the widget that initiated this even, in this case it is the log listbox
        self.logIndex = self.logListBox.curselection()[0]
        if self.tabNum == 0:
            self.summaryButtonCommand()
        elif self.tabNum == 1:
            self.launchInfoButtonCommand()
        elif self.tabNum == 2:
            self.contentsButtonCommand()
        elif self.tabNum == 3:
            self.logStatsButtonCommand()
        elif self.tabNum == 4:
            self.globalStatsButtonCommand()


    def updateDetailTextBoxToLaunchInfo(self):

        # get the logfile date and time from the listbox
        value = self.logListBox.get(self.logIndex).split()
        # get the log object from the logManager object associated with this class
        log = self.allEntries.getLog(value[0], value[1])
        # update the textbox to the contents of the selected log file
        self.detailText.config(state=NORMAL)
        self.detailText.delete('1.0', END)
        self.detailText.insert(INSERT, log.launchInfo.getAll())
        self.detailText.config(state=DISABLED)


    def updateDetailTextBoxToSummary(self):

        # get the logfile date and time from the listbox
        value = self.logListBox.get(self.logIndex).split()
        # get the log object from the logManager object associated with this class
        log = self.allEntries.getLog(value[0], value[1])
        # update the textbox to the contents of the selected log file
        self.detailText.config(state=NORMAL)
        self.detailText.delete('1.0', END)
        self.detailText.insert(INSERT, log.logSummaryToString())
        self.detailText.config(state=DISABLED)

    def updateDetailBoxToContents(self):
        # get the logfile date and time from the listbox
        value = self.logListBox.get(self.logIndex).split()
        # get the log object from the logManager object associated with this class
        log = self.allEntries.getLog(value[0], value[1])
        # update the textbox to the contents of the selected log file
        self.detailText.config(state=NORMAL)
        self.detailText.delete('1.0', END)
        if log.allLogsToString() == "":
            self.detailText.insert(INSERT, "Failed to Launch. Check \"Launch Info\" tab for all entries of the log file.")
        else:
            self.detailText.insert(INSERT, log.allLogsToString())
        self.detailText.config(state=DISABLED)

    def updateDetailBoxToLocalStats(self):
        # get the logfile date and time from the listbox
        value = self.logListBox.get(self.logIndex).split()
        # get the log object from the logManager object associated with this class
        log = self.allEntries.getLog(value[0], value[1])
        # update the textbox to the contents of the selected log file
        self.detailText.config(state=NORMAL)
        self.detailText.delete('1.0', END)
        self.detailText.insert(INSERT, log.stats.toString())
        self.detailText.config(state=DISABLED)

    def updateDetailBoxToGlobalStats(self):
        self.detailText.config(state=NORMAL)
        self.detailText.delete('1.0', END)
        self.detailText.insert(INSERT, self.allEntries.getStats())
        self.detailText.config(state=DISABLED)

    # add the log filenames from the logManager object to the log listbox
    def addToLogFileList(self,list):
        for log in list.logList:
            self.logListBox.insert(END,log.date+" "+log.time)

    def summaryButtonCommand(self):
        if self.logIndex != -1:
            self.summaryButton.config(bg="#a3a3a3")
            self.launchInfoButton.config(bg="#d3d3d3")
            self.contentsButton.config(bg="#d3d3d3")
            self.logStatsButton.config(bg="#d3d3d3")
            self.globalStatsButton.config(bg="#d3d3d3")
            self.updateDetailTextBoxToSummary()
            self.tabNum = 0


    def launchInfoButtonCommand(self):
        if self.logIndex != -1:
            self.launchInfoButton.config(bg="#a3a3a3")
            self.summaryButton.config(bg="#d3d3d3")
            self.contentsButton.config(bg="#d3d3d3")
            self.logStatsButton.config(bg="#d3d3d3")
            self.globalStatsButton.config(bg="#d3d3d3")
            self.updateDetailTextBoxToLaunchInfo()
            self.tabNum = 1


    def contentsButtonCommand(self):
        if self.logIndex != -1:
            self.contentsButton.config(bg="#a3a3a3")
            self.summaryButton.config(bg="#d3d3d3")
            self.launchInfoButton.config(bg="#d3d3d3")
            self.logStatsButton.config(bg="#d3d3d3")
            self.globalStatsButton.config(bg="#d3d3d3")
            self.updateDetailBoxToContents()
            self.tabNum = 2

    def logStatsButtonCommand(self):
        if self.logIndex != -1:
            self.logStatsButton.config(bg="#a3a3a3")
            self.summaryButton.config(bg="#d3d3d3")
            self.launchInfoButton.config(bg="#d3d3d3")
            self.contentsButton.config(bg="#d3d3d3")
            self.globalStatsButton.config(bg="#d3d3d3")
            self.updateDetailBoxToLocalStats()
            self.tabNum = 3

    def globalStatsButtonCommand(self):
        self.globalStatsButton.config(bg="#a3a3a3")
        self.summaryButton.config(bg="#d3d3d3")
        self.launchInfoButton.config(bg="#d3d3d3")
        self.contentsButton.config(bg="#d3d3d3")
        self.logStatsButton.config(bg="#d3d3d3")
        self.updateDetailBoxToGlobalStats()
        self.tabNum = 4

class logFileWindow:
    def __init__(self):
        self.root = Tk()
        lb = Listbox(self.root)
        lb.pack()
        self.root.mainloop()

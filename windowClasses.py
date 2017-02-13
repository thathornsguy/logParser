from Tkinter import *
import datastorage
import os
import tkFileDialog

class bootWindow:
    def __init__(self,allEntries):
        # index of the currently selected log
        self.logIndex = 0
        # the logManager object associated with the found log files
        self.allEntries = allEntries
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
        mainSpacer = Frame(mainFrame,width=int(self.width/100))

        # the grame containing the details textbox and the x and y scroll bars for that textbox
        detailFrame = Frame(mainFrame)
        # the detail tabs frame
        buttonTabFrame = Frame(detailFrame)
        buttonSpacer = Frame(buttonTabFrame, width=int(self.width/2.1))
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
        self.summaryButton = Button(buttonTabFrame,command = self.summaryButtonCommand, text="Log Summary",bg="#a3a3a3")
        self.launchInfoButton = Button(buttonTabFrame,command = self.launchInfoButtonCommand, text="Launch Info",bg="#d3d3d3")
        self.contentsButton = Button(buttonTabFrame,command = self.contentsButtonCommand, text="Log Contents",bg="#d3d3d3")
        self.logStatsButton = Button(buttonTabFrame,command = self.logStatsButtonCommand, text="Log Stats",bg="#d3d3d3")
        self.globalStatsButton = Button(buttonTabFrame,command = self.globalStatsButtonCommand, text="Global Stats",bg="#d3d3d3")

        # the current button that is pressed, default is the summary tab
        self.currButton = self.summaryButton

        # add the buttons to the window
        self.summaryButton.pack(side="left")
        self.launchInfoButton.pack(side="left")
        self.contentsButton.pack(side="left")
        self.logStatsButton.pack(side="left")
        self.globalStatsButton.pack(side="left")
        buttonSpacer.pack(side="right")
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
        fileMenu = Menu(m,tearoff=0)
        fileMenu.add_command(label="Change Directory...",command=self.changeDirectory)
        m.add_cascade(label="File",menu = fileMenu)
        # add the menu to the main window
        self.root.config(menu=m)
        # add all the log files found in the specified directory to the listbox
        self.addToLogFileList(allEntries)
        # the logic that changes the textbox to the contents of the selected log file
        self.logListBox.bind('<<ListboxSelect>>', self.updateSelection)
        # override what happens after the x button is hit to close the window
        self.root.protocol('WM_DELETE_WINDOW',exit)
        # causes the window to open
        self.root.mainloop()

    # called when the changed directory menu option is clicked
    def changeDirectory(self):
        # update the logManager object
        returnCode = self.allEntries.update()
        # if no directory was chosen do nothing
        if returnCode == 1:
            return
        # change the button colors back to default
        self.summaryButton.config(bg="#d3d3d3")
        self.launchInfoButton.config(bg="#d3d3d3")
        self.contentsButton.config(bg="#d3d3d3")
        self.logStatsButton.config(bg="#d3d3d3")
        self.globalStatsButton.config(bg="#d3d3d3")
        # delete contents of the detail textbox
        self.detailText.config(state=NORMAL)
        self.detailText.delete("1.0", END)
        self.detailText.config(state=DISABLED)
        # delete all entries in the listbox
        self.logListBox.delete(0, END)
        # add all the new entries to the listbox
        self.addToLogFileList(self.allEntries)

    # when a log is selected from the listbox update the textbox to the contents of the associated log
    def updateSelection(self,evt):
        # get the currently selected tab index
        self.logIndex = self.logListBox.curselection()[0]
        # update the textbox based on the currently selected tab
        self.currButton.invoke()

    # inserts the string toPut into the textbox on the right side of the window
    def updateTextBox(self,toPut):
        self.detailText.config(state=NORMAL)
        self.detailText.delete('1.0', END)
        self.detailText.insert(INSERT, toPut)
        self.detailText.config(state=DISABLED)

    # gets the log object associated with the currently selected log in the logListBox
    def getLog(self):
        # get the logfile date and time from the listbox
        value = self.logListBox.get(self.logIndex).split()
        # get the log object from the logManager object associated with this class
        return self.allEntries.getLog(value[0], value[1])


    # add the log filenames from the logManager object to the log listbox
    def addToLogFileList(self,list):
        for log in list.logList:
            self.logListBox.insert(END,log.date+" "+log.time)
        self.logListBox.selection_set(0)
        self.updateSelection(None)


    # change the colors of the buttons and update the textbox to the summary information
    def summaryButtonCommand(self):
        log = self.getLog()
        self.updateTextBox(log.logSummaryToString())
        self.updateCurrButton(self.summaryButton)


    # change the colors of the buttons and update the textbox to the summary information
    def launchInfoButtonCommand(self):
        log = self.getLog()
        self.updateTextBox(log.launchInfo.getAll())
        self.updateCurrButton(self.launchInfoButton)

    # change the colors of the buttons and update the textbox to the summary information
    def contentsButtonCommand(self):
        log = self.getLog()
        self.updateTextBox(log.allLogsToString())
        self.updateCurrButton(self.contentsButton)

    # change the colors of the buttons and update the textbox to the summary information
    def logStatsButtonCommand(self):
        log = self.getLog()
        self.updateTextBox(log.stats.toString())
        self.updateCurrButton(self.logStatsButton)

    # change the colors of the buttons and update the textbox to the summary information
    def globalStatsButtonCommand(self):
        log = self.getLog()
        self.updateTextBox(self.allEntries.getStats())
        self.updateCurrButton(self.globalStatsButton)

    def updateCurrButton(self,nextButton):
        self.currButton.config(bg="#d3d3d3")
        nextButton.config(bg="#a3a3a3")
        self.currButton = nextButton
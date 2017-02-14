from Tkinter import *

class filterWindow:
    def __init__(self, currFilter):
        self.root=Toplevel()
        self.filter = currFilter
        c = Checkbutton(self.root,variable=self.filter.enabled)
        c.grid(column=2,row=1)
        checkButtonLabel = Label(self.root,text="Enable: ")
        checkButtonLabel.grid(column=1,row=1)
        dateLabel = Label(self.root,text="Date:")
        dateLabel.grid(column=1,row=2)
        startDateEntry = Entry(self.root,textvariable=self.filter.startDate,width=10)
        startDateEntry.grid(column=2,row=2,padx=5)
        dateLabelSpacer = Label(self.root, text="to")
        dateLabelSpacer.grid(column=3, row=2)
        endDateEntry = Entry(self.root, textvariable=self.filter.endDate, width=10)
        endDateEntry.grid(column=4, row=2,padx=5)
        self.root.mainloop()


class filter:
    def __init__(self):
        self.enabled = False
        self.startDate = StringVar()
        self.endDate = StringVar()
        self.startDate.set("00/00/00")
        self.endDate.set("00/00/00")

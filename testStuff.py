from Tkinter import *

def onselect(evt):
    # Note here that Tkinter passes an event object to onselect()
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    print 'You selected item %d: "%s"' % (index, value)

root = Tk()
f = Frame(root)
lb = Listbox(f, name='lb')
lb.insert(END,"test")
lb.pack()
f.pack()
lb.bind('<<ListboxSelect>>', onselect)
root.mainloop()

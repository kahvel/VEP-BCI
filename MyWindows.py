__author__ = 'Anti'

from Tkinter import Tk, Toplevel, Label, Entry


class TkWindow(Tk):

    def __init__(self, title, width, height, color="#eeeeee"):
        Tk.__init__(self)
        self.title(title)
        self.geometry(str(width)+"x"+str(height))
        self.resizable(0,0)
        self.configure(background=color)

        #self.protocol("WM_DELETE_WINDOW", self.exit)

    def exit(self):
        self.destroy() #quit siia

    def focus(self):
        #self.focus_set() # not working. Load crashes...
        #self.grab_set()
        #self.transient(parent)
        self.wait_window(self)

class ToplevelWindow(Toplevel):

    def __init__(self, title, width, height, color="#eeeeee"):
        Toplevel.__init__(self)
        self.title(title)
        self.geometry(str(width)+"x"+str(height))
        self.resizable(0,0)
        self.configure(background=color)
        #self.protocol("WM_DELETE_WINDOW", self.iconify)


    def setProtocol(self, name, function):
        self.protocol(name, function)
    def a(self):
        print "jou"

    def exit(self):
        self.destroy()

    def focus(self):
        #self.focus_set() # not working. Load crashes...
        #self.grab_set()
        #self.transient(parent)
        self.wait_window(self)

def newTextBox(frame, text, column, row, width=5):
    Label(frame, text=text).grid(column=column, row=row, padx=5, pady=5)
    textbox = Entry(frame, width=width)
    textbox.grid(column=column+1, row=row, padx=5, pady=5)
    return textbox


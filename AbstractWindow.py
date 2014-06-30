__author__ = 'Anti'

from Tkinter import Toplevel, Label, Entry

class Window(object):
    def __init__(self, title, width, height, color="#eeeeee", window=Toplevel):
        self.height = height
        self.width = width
        self.window = window()
        self.window.title(title)
        self.window.geometry(str(self.width)+"x"+str(self.height))
        self.window.resizable(0,0)
        self.window.configure(background=color)

    def newTextBox(self, frame, text, column, row, width=5):
        Label(frame, text=text).grid(column=column, row=row, padx=5, pady=5)
        textbox = Entry(frame, width=width)
        textbox.grid(column=column+1, row=row, padx=5, pady=5)
        return textbox

    def exit(self):
        self.window.destroy()

    def focus(self):
        #self.window.focus_set() # not working. Load crashes...
        #self.window.grab_set()
        #self.window.transient(parent)
        self.window.wait_window(self.window)
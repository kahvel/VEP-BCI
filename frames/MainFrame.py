__author__ = 'Anti'

from frames import Frame
from notebooks import MainNotebook
from widgets import Buttons


class MainFrame(Frame.Frame):
    def __init__(self, parent, start, save, load, exit, row=0, column=0, **kwargs):
        Frame.Frame.__init__(self, parent, "MainFrame", row, column, **kwargs)
        self.addChildWidgets((
            MainNotebook.MainNotebook(self.widget, 0, 0),
            BottomFrame(self.widget, start, save, load, exit, 1, 0)
        ))


class BottomFrame(Frame.Frame):
    def __init__(self, parent, start, save, load, exit, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, "BottomFrame", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self.widget, "Start", 0, 0, command=start),
            Buttons.Button(self.widget, "Save",  0, 1, command=save),
            Buttons.Button(self.widget, "Load",  0, 2, command=load),
            Buttons.Button(self.widget, "Exit",  0, 3, command=exit)
        ))
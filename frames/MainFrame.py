__author__ = 'Anti'

from frames import Frame
from notebooks import MainNotebook
from widgets import Buttons


class MainFrame(Frame.Frame):
    def __init__(self, start, save, load, exit, row=0, column=0, **kwargs):
        Frame.Frame.__init__(self, "MainFrame", row, column, **kwargs)
        self.addChildWidgets((
            MainNotebook.MainNotebook(0, 0),
            BottomFrame(start, save, load, exit, 1, 0)
        ))


class BottomFrame(Frame.Frame):
    def __init__(self, start, save, load, exit, row, column, **kwargs):
        Frame.Frame.__init__(self, "BottomFrame", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button("Start", 0, 0, command=start),
            Buttons.Button("Save",  0, 1, command=save),
            Buttons.Button("Load",  0, 2, command=load),
            Buttons.Button("Exit",  0, 3, command=exit)
        ))
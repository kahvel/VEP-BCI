__author__ = 'Anti'

from frames import Frame
from notebooks import MainNotebook
from widgets import Buttons


class MainFrame(Frame.Frame):
    def __init__(self, start, save, load, exit, row=0, column=0, columnspan=1, padx=0, pady=0):
        Frame.Frame.__init__(self, "MainFrame", row, column, columnspan, padx, pady)
        self.addChildWidgets((
            MainNotebook.MainNotebook(0, 0, 1, 0, 0),
            BottomFrame(start, save, load, exit, row=1)
        ))


class BottomFrame(Frame.Frame):
    def __init__(self, start, save, load, exit, row=0, column=0, columnspan=1, padx=0, pady=0):
        Frame.Frame.__init__(self, "BottomFrame", row, column, columnspan, padx, pady)
        self.addChildWidgets((
            Buttons.Button("Start", 0, 0, start, command_on_load=False),
            Buttons.Button("Save",  0, 1, save,  command_on_load=False),
            Buttons.Button("Load",  0, 2, load,  command_on_load=False),
            Buttons.Button("Exit",  0, 3, exit,  command_on_load=False)
        ))
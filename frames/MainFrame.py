__author__ = 'Anti'

from frames import Frame
from notebooks import MainNotebook
from widgets import Buttons
import Constants as c


class MainFrame(Frame.Frame):
    def __init__(self, parent, start, save, load, exit, row=0, column=0, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            MainNotebook.MainNotebook(self.widget, 0, 0),
            BottomFrame(self.widget, start, save, load, exit, 1, 0)
        ))


class BottomFrame(Frame.Frame):
    def __init__(self, parent, start, save, load, exit, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.BOTTOM_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self.widget, c.START_BUTTON, 0, 0, command=start),
            Buttons.Button(self.widget, c.SAVE_BUTTON,  0, 1, command=save),
            Buttons.Button(self.widget, c.LOAD_BUTTON,  0, 2, command=load),
            Buttons.Button(self.widget, c.EXIT_BUTTON,  0, 3, command=exit)
        ))
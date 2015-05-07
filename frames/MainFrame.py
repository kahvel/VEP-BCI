__author__ = 'Anti'

from frames import Frame
from notebooks import MainNotebook
from widgets import Buttons
import constants as c


class MainFrame(Frame.Frame):
    def __init__(self, parent, bottom_frame_buttons, notebook_buttons, row=0, column=0, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            MainNotebook.MainNotebook(self.widget, notebook_buttons, 0, 0),
            BottomFrame(self.widget, bottom_frame_buttons, 1, 0)
        ))


class BottomFrame(Frame.Frame):
    def __init__(self, parent, buttons, row, column, **kwargs):
        start, stop, setup, save, load, exit = buttons
        Frame.Frame.__init__(self, parent, c.BOTTOM_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self.widget, c.START_BUTTON, 0, 0, command=start),
            Buttons.Button(self.widget, c.STOP_BUTTON,  0, 1, command=stop),
            Buttons.Button(self.widget, c.SETUP_BUTTON, 0, 2, command=setup),
            Buttons.Button(self.widget, c.SAVE_BUTTON,  0, 3, command=save),
            Buttons.Button(self.widget, c.LOAD_BUTTON,  0, 4, command=load),
            Buttons.Button(self.widget, c.EXIT_BUTTON,  0, 5, command=exit)
        ))

    def disableButton(self, button_name):
        self.widgets_dict[button_name].disable("PostOffice")

    def enableButton(self, button_name):
        self.widgets_dict[button_name].enable("PostOffice")

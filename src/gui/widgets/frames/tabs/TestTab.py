__author__ = 'Anti'

import Tkinter

from gui.widgets.frames import Frame
from gui.widgets import OptionMenu, Checkbutton, Buttons, Textboxes
import constants as c


class ResultsFrame(Frame.Frame):
    def __init__(self, parent, buttons, row, column, **kwargs):
        show, reset, save = buttons
        Frame.Frame.__init__(self, parent, c.RESULT_FRAME, row, column, **kwargs)
        Tkinter.Label(self.widget, text="Results").grid(row=0, column=0, padx=5, pady=5)
        self.addChildWidgets((
            Buttons.Button(self.widget, c.RESULT_SHOW_BUTTON,  0, 1, command=show),
            Buttons.Button(self.widget, c.RESULT_RESET_BUTTON, 0, 2, command=reset),
            Buttons.Button(self.widget, c.RESULT_SAVE_BUTTON, 0, 3, command=save)
        ))


class TestTab(Frame.Frame):
    def __init__(self, parent, buttons, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.TEST_TAB, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.TargetChoosingMenu(self.widget, c.TEST_TARGET,    0, 1, (c.TEST_NONE, c.TEST_RANDOM), columnspan=2),
            Textboxes.ColorTextboxFrame(self.widget, c.TEST_COLOR, c.TEST_COLOR_FRAME, 0, 3, default_value="#ffffb3"),
            OptionMenu.TargetChoosingMenu(self.widget, c.TEST_STANDBY,   1, 1, (c.TEST_NONE,), columnspan=2),
            Textboxes.LabelTextbox(self.widget, c.TEST_TIME,      2, 0, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_UNLIMITED]),
            Checkbutton.Checkbutton(self.widget, c.TEST_UNLIMITED, 2, 2, columnspan=2, command=self.enableTime, default_value=1),
            ResultsFrame(self.widget, buttons, 4, 0, columnspan=4)
        ))

    def enableTime(self):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_UNLIMITED],
            (0,),
            (self.widgets_dict[c.TEST_TIME],)
        )

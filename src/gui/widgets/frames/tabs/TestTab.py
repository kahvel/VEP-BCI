import Tkinter

from gui.widgets.frames import Frame
from gui.widgets import OptionMenu, Checkbutton, Buttons, Textboxes
import constants as c
import Savable


class ResultsFrame(Frame.Frame, Savable.Savable):
    def __init__(self, parent, buttons, row, column, **kwargs):
        show, reset, save = buttons
        self.main_window_save_results_function = save
        Frame.Frame.__init__(self, parent, c.RESULT_FRAME, row, column, no_value=True, **kwargs)
        Tkinter.Label(self.widget, text="Results").grid(row=0, column=0, padx=5, pady=5)
        self.addChildWidgets((
            Buttons.Button(self, c.RESULT_SHOW_BUTTON,  0, 1, command=show),
            Buttons.Button(self, c.RESULT_RESET_BUTTON, 0, 2, command=reset),
            Buttons.Button(self, c.RESULT_SAVE_BUTTON, 0, 3, command=self.askSaveFile)
        ))

    def saveToFile(self, file):
        self.main_window_save_results_function(file)


class TestTab(Frame.Frame):
    def __init__(self, parent, buttons, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.TEST_TAB, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.TargetChoosingMenu(self, c.TEST_TARGET,    0, 1, (c.TEST_NONE, c.TEST_RANDOM, c.TEST_TIMED), columnspan=2),
            Textboxes.ColorTextboxFrame(self, c.TEST_COLOR, 0, 3, default_value="#ffffb3"),
            OptionMenu.TargetChoosingMenu(self, c.TEST_STANDBY,   1, 1, (c.TEST_NONE,), columnspan=2),
            Textboxes.LabelTextbox(self, c.TEST_TIME,      2, 0, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_UNLIMITED]),
            Checkbutton.Checkbutton(self, c.TEST_UNLIMITED, 2, 2, columnspan=2, command=self.enableTime, default_value=1),
            ResultsFrame(self, buttons, 4, 0, columnspan=4),
            IdentificationOptionsFrame(self, 5, 0, columnspan=4)
        ))

    def enableTime(self):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_UNLIMITED],
            (0,),
            (self.widgets_dict[c.TEST_TIME],)
        )


class IdentificationOptionsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.IDENTIFICATION_OPTIONS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Checkbutton.Checkbutton(self, c.TEST_CLEAR_BUFFERS,             0, 0),
            Checkbutton.Checkbutton(self, c.TEST_PROCESS_SHORT_SIGNALS,     1, 0),
            ResultCounterFrame     (self, c.TEST_RESULT_COUNTER_FRAME,      2, 0, columnspan=2),
            ResultCounterFrame     (self, c.TEST_PREV_RESULT_COUNTER_FRAME, 3, 0, columnspan=2),
        ))


class ResultCounterFrame(Frame.Frame):
    def __init__(self, parent, name, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, column, **kwargs)
        Tkinter.Label(self.widget, text=name).grid(row=0, column=0)
        self.addChildWidgets((
            Checkbutton.Checkbutton(self, c.TEST_ALWAYS_DELETE,    0, 2, columnspan=2),
            Textboxes.LabelTextbox (self, c.TEST_RESULT_COUNTER,   1, 0, default_value=1),
            Textboxes.LabelTextbox (self, c.TEST_RESULT_THRESHOLD, 1, 2, allow_zero=True),
        ))

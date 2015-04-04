__author__ = 'Anti'

from widgets import Textboxes, Checkbutton, OptionMenu
from frames import Frame


class TestTab(Frame.Frame):
    def __init__(self, parent, row, column, target_notebook, **kwargs):
        Frame.Frame.__init__(self, parent, "Test", row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.LabelTextbox (self.widget, "Length",  0, 0, command=int, default_value=1),
            Textboxes.LabelTextbox (self.widget, "Min",     0, 2, command=int, default_value=1),
            Textboxes.LabelTextbox (self.widget, "Max",     0, 4, command=int, default_value=1),
            Checkbutton.Checkbutton(self.widget, "Random",  1, 0, columnspan=2),
            Checkbutton.Checkbutton(self.widget, "Standby", 1, 2, columnspan=2),
            OptionMenu.OptionMenu  (self.widget, "Testing", 2, 0, columnspan=2, values=("None", "Random", 1))
        ))


__author__ = 'Anti'

from widgets import Textboxes, Checkbutton
from frames import Frame


class TestTab(Frame.Frame):
    def __init__(self, row, column, columnspan, padx, pady):
        Frame.Frame.__init__(self, "Test", row, column, columnspan, padx, pady)
        self.addChildWidgets((
            Textboxes.LabelTextbox ("Length",  0, 0, int, False, False, default_value=1),
            Textboxes.LabelTextbox ("Min",     0, 2, int, False, False, default_value=1),
            Textboxes.LabelTextbox ("Max",     0, 4, int, False, False, default_value=1),
            Checkbutton.Checkbutton("Random",  1, 0, columnspan=2),
            Checkbutton.Checkbutton("Standby", 1, 2, columnspan=2)
        ))
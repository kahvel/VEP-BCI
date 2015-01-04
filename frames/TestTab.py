__author__ = 'Anti'

from widgets import Textboxes, Checkbutton
from frames import Frame


class TestTab(Frame.Frame):
    def __init__(self, row, column, **kwargs):
        Frame.Frame.__init__(self, "Test", row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.LabelTextbox ("Length",  0, 0, command=int, default_value=1),
            Textboxes.LabelTextbox ("Min",     0, 2, command=int, default_value=1),
            Textboxes.LabelTextbox ("Max",     0, 4, command=int, default_value=1),
            Checkbutton.Checkbutton("Random",  1, 0, columnspan=2),
            Checkbutton.Checkbutton("Standby", 1, 2, columnspan=2)
        ))
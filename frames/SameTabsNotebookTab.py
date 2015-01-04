__author__ = 'Anti'

from widgets import Buttons
from frames import Frame


class SameTabsNotebookTab(Frame.Frame):
    def __init__(self, name, row, column, **kwargs):
        Frame.Frame.__init__(self, name, row, column, **kwargs)
        #self.delete_tab = kwargs["delete_tab"]

    def getDisableDeleteFrame(self, row, column, **kwargs):
        disable_tab = lambda: self.changeState("Disable")
        return DisableDeleteFrame(row, column, disable_tab=disable_tab, **kwargs)


class DisableDeleteFrame(Frame.Frame):
    def __init__(self, row, column, **kwargs):
        Frame.Frame.__init__(self, "DisableDeleteFrame", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton("Disable", 0, 0, command=kwargs["disable_tab"], always_enabled=True),
            Buttons.Button      ("Delete",  0, 1, command=kwargs["delete_tab"],  always_enabled=True)
        ))
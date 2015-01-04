__author__ = 'Anti'

from widgets import Buttons
from frames import Frame


class SameTabsNotebookTab(Frame.Frame):
    def __init__(self, name, row, column, **kwargs):
        Frame.Frame.__init__(self, name, row, column, **kwargs)

    def getDisableDeleteFrame(self, row, column, **kwargs):
        return DisableDeleteFrame(row, column, disable=self.disable, enable=self.enable, **kwargs)


class DisableDeleteFrame(Frame.Frame):
    def __init__(self, row, column, **kwargs):
        Frame.Frame.__init__(self, "DisableDeleteFrame", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.DisableButton("Disable", 0, 0, enable=kwargs["enable"], disable=kwargs["disable"], always_enabled=True),
            Buttons.Button      ("Delete",  0, 1, command=kwargs["delete_tab"],  always_enabled=True)
        ))
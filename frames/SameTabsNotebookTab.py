__author__ = 'Anti'

from widgets import Buttons
from frames import Frame


class SameTabsNotebookTab(Frame.Frame):
    def __init__(self, parent, name, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, column, **kwargs)

    def getDisableDeleteFrame(self, row, column, **kwargs):
        return DisableDeleteFrame(self.widget, row, column, disable=self.disable, enable=self.enable, **kwargs)


class DisableDeleteFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, "DisableDeleteFrame", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.DisableButton(self.widget, "Disable", 0, 0, enable=kwargs["enable"], disable=kwargs["disable"], always_enabled=True),
            Buttons.Button       (self.widget, "Delete",  0, 1, command=kwargs["delete_tab"],  always_enabled=True)
        ))
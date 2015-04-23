__author__ = 'Anti'

from widgets import Buttons
from frames import Frame
import constants as c


class DisableDeleteNotebookTab(Frame.Frame):
    def __init__(self, parent, name, **kwargs):
        Frame.Frame.__init__(self, parent, name, 0, 0, **kwargs)

    def getDisableDeleteFrame(self, row, column, **kwargs):
        return DisableDeleteFrame(self.widget, row, column, disable=self.disable, enable=self.enable, **kwargs)


class Disable(Frame.Frame):
    def __init__(self, parent, name, **kwargs):
        Frame.Frame.__init__(self, parent, name, 0, 0, **kwargs)

    def getDisableButton(self, row, column, **kwargs):
        return Buttons.DisableButton(self.widget, c.DISABLE_METHOD, row, column, enable=self.enable, disable=self.disable, always_enabled=True)


class DisableDeleteFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.DISABLE_DELETE_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.DisableButton(self.widget, c.DISABLE, 0, 0, enable=kwargs["enable"], disable=kwargs["disable"], always_enabled=True),
            Buttons.Button       (self.widget, c.DELETE,  0, 1, command=kwargs["delete_tab"],  always_enabled=True)
        ))

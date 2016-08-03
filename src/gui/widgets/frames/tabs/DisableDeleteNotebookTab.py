from gui.widgets import Buttons
from gui.widgets.frames import Frame
import constants as c


class DisableDeleteNotebookTab(Frame.Frame):
    def __init__(self, parent, name, **kwargs):
        Frame.Frame.__init__(self, parent, name, 0, 0, **kwargs)

    def getDisableDeleteFrame(self, row, column, deleteTab, **kwargs):
        return DisableDeleteFrame(self, row, column, deleteTab, disable=self.disable, enable=self.enable, **kwargs)


class Disable(Frame.Frame):
    def __init__(self, parent, name, **kwargs):
        Frame.Frame.__init__(self, parent, name, 0, 0, **kwargs)

    def getDisableButton(self, row, column, **kwargs):
        return Buttons.DisableButton(self, c.DISABLE, row, column, enable=self.enable, disable=self.disable, always_enabled=True)


class Delete(Frame.Frame):
    def __init__(self, parent, name, **kwargs):
        Frame.Frame.__init__(self, parent, name, 0, 0, **kwargs)

    def getDeleteButton(self, row, column, deleteTab, **kwargs):
        return Buttons.Button(self, c.DELETE, row, column, command=deleteTab, always_enabled=True)


class DisableDeleteFrame(Frame.Frame):
    def __init__(self, parent, row, column, deleteTab, **kwargs):
        Frame.Frame.__init__(self, parent, c.DISABLE_DELETE_FRAME, row, column, no_value=True, **kwargs)
        self.addChildWidgets((
            Buttons.DisableButton(self, c.DISABLE, 0, 0, enable=kwargs["enable"], disable=kwargs["disable"], always_enabled=True),
            Buttons.Button       (self, c.DELETE,  0, 1, command=deleteTab,  always_enabled=True)
        ))

__author__ = 'Anti'

from widgets import Frame, Buttons


class SameTabsNotebookTab(Frame.Frame):
    def __init__(self, name, row, column, columnspan, padx, pady, delete_tab):
        Frame.Frame.__init__(self, name, row, column, columnspan, padx, pady)
        self.delete_tab = delete_tab

    def getDisableDeleteFrame(self, row, column, columnspan, padx, pady):
        disable_tab = lambda: self.changeState("Disable")
        return DisableDeleteFrame(row, column, columnspan, padx, pady, self.delete_tab, disable_tab)


class DisableDeleteFrame(Frame.Frame):
    def __init__(self, row, column, columnspan, padx, pady, delete_tab, disable_tab):
        Frame.Frame.__init__(self, "DisableDeleteFrame", row, column, columnspan, padx, pady)
        self.addChildWidgets((
            Buttons.SunkenButton("Disable", 0, 0, disable_tab, command_on_load=False, always_enabled=True),
            Buttons.Button      ("Delete",  0, 1, delete_tab,  command_on_load=False, always_enabled=True)
        ))
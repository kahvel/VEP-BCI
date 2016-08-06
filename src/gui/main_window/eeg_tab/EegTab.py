from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
from gui_elements.widgets.frames import Frame
from gui_elements.widgets import OptionMenu
import constants as c


class EegTab(DisableDeleteNotebookTab.Disable):
    def __init__(self, parent, **kwargs):
        DisableDeleteNotebookTab.Disable.__init__(self, parent, c.EEG_TAB)
        self.addChildWidgets((
            self.getDisableButton(0, 0),
        ))


class EegTabFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.EEG_TAB_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self, c.EEG_TAB_EEG_SOURCE_OPTION_MENU, 0, 0, c.EEG_SOURCE_NAMES),
        ))

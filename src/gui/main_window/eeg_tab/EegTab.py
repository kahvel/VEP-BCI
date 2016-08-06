from gui_elements.widgets.frames import Frame, AddingCheckbuttonsFrame
from gui_elements.widgets import OptionMenu
import constants as c


class CheckbuttonFrame(AddingCheckbuttonsFrame.AddingCheckbuttonsFrame):
    def __init__(self, parent, row, column, **kwargs):
        AddingCheckbuttonsFrame.AddingCheckbuttonsFrame.__init__(self, parent, c.EEG_TAB_ADDING_CHECKBUTTON_FRAME, row, column, [], **kwargs)

    def trialEndedEvent(self):
        self.addButton()

    def recordTabRemoved(self, deleted_tab):
        self.deleteButton(deleted_tab)

    def loadEegEvent(self, directory):
        self.addButton()


class EegTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.EEG_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self, c.EEG_TAB_EEG_SOURCE_OPTION_MENU, 0, 1, c.EEG_SOURCE_NAMES),
            CheckbuttonFrame(self, 1, 0, columnspan=3),
        ))

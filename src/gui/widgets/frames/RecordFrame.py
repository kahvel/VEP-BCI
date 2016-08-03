from gui.widgets import OptionMenu
from gui.widgets.frames import Frame
from gui.widgets.frames.notebooks import SameTabsNotebook

import constants as c


class RecordFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.RECORD_TAB_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenuFrame(self, c.TRAINING_RECORD, 0, 0, c.TRAINING_RECORD_NAMES),
            SameTabsNotebook.ResultsNotebook(self, 1, 0)
        ))

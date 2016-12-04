from gui_elements.widgets import OptionMenu
from gui_elements.widgets.frames import Frame
import constants as c
import Savable


class TrainingTab(Frame.Frame, Savable.Savable, Savable.Loadable):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_TRAINING_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self, c.TRAINING_METHOD, 2, 1, c.TRAINING_METHOD_NAMES),
        ))

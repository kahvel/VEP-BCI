from gui.widgets import OptionMenu
from gui.widgets.frames import Frame
import constants as c
import Savable


class TrainingTab(Frame.Frame, Savable.Savable, Savable.Loadable):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.TRAINING_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self.widget, c.TRAINING_METHOD, 2, 1, c.TRAINING_METHOD_NAMES),
        ))

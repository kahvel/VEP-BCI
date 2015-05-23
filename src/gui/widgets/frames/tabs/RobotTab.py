__author__ = 'Anti'

from gui.widgets.frames import Frame
from gui.widgets import Buttons, OptionMenu
import constants as c


class RobotTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.ROBOT_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self.widget, c.ROBOT_OPTION_FORWARD, 0, 1, (c.ROBOT_NONE,)),
            OptionMenu.OptionMenu(self.widget, c.ROBOT_OPTION_BACKWARD, 1, 1, (c.ROBOT_NONE,)),
            OptionMenu.OptionMenu(self.widget, c.ROBOT_OPTION_RIGHT, 2, 1, (c.ROBOT_NONE,)),
            OptionMenu.OptionMenu(self.widget, c.ROBOT_OPTION_LEFT, 3, 1, (c.ROBOT_NONE,)),
            OptionMenu.OptionMenu(self.widget, c.ROBOT_OPTION_STOP, 4, 1, (c.ROBOT_NONE,))
        ))

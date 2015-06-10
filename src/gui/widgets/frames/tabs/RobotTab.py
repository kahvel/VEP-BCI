from gui.widgets.frames.tabs import DisableDeleteNotebookTab
from gui.widgets.frames import Frame
from gui.widgets import Buttons, OptionMenu, Checkbutton, Textboxes
import constants as c


class RobotTab(DisableDeleteNotebookTab.Disable):
    def __init__(self, parent, sendMessage, **kwargs):
        Frame.Frame.__init__(self, parent, c.ROBOT_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionMenu.TargetChoosingMenu(self.widget, c.ROBOT_OPTION_FORWARD, 0, 1, (c.ROBOT_NONE,)),
            OptionMenu.TargetChoosingMenu(self.widget, c.ROBOT_OPTION_BACKWARD, 1, 1, (c.ROBOT_NONE,)),
            OptionMenu.TargetChoosingMenu(self.widget, c.ROBOT_OPTION_RIGHT, 2, 1, (c.ROBOT_NONE,)),
            OptionMenu.TargetChoosingMenu(self.widget, c.ROBOT_OPTION_LEFT, 3, 1, (c.ROBOT_NONE,)),
            OptionMenu.TargetChoosingMenu(self.widget, c.ROBOT_OPTION_STOP, 4, 1, (c.ROBOT_NONE,)),
            Buttons.Button(self.widget, c.ROBOT_TEST, 0, 3, command=lambda: sendMessage(c.MOVE_FORWARD)),
            Buttons.Button(self.widget, c.ROBOT_TEST, 1, 3, command=lambda: sendMessage(c.MOVE_BACKWARD)),
            Buttons.Button(self.widget, c.ROBOT_TEST, 2, 3, command=lambda: sendMessage(c.MOVE_RIGHT)),
            Buttons.Button(self.widget, c.ROBOT_TEST, 3, 3, command=lambda: sendMessage(c.MOVE_LEFT)),
            Buttons.Button(self.widget, c.ROBOT_TEST, 4, 3, command=lambda: sendMessage(c.MOVE_STOP)),
            Textboxes.LabelTextbox(self.widget, c.STREAM_X, 5, 0, command=int, allow_negative=True, allow_zero=True),
            Textboxes.LabelTextbox(self.widget, c.STREAM_Y, 5, 2, command=int, allow_negative=True, allow_zero=True),
            Checkbutton.Checkbutton(self.widget, c.ROBOT_STREAM, 5, 4, command=self.enableCoordinates, default_value=1),
            Textboxes.LabelTextbox(self.widget, c.STREAM_WIDTH, 6, 0, command=int, allow_negative=True, allow_zero=True, default_value=320),
            Textboxes.LabelTextbox(self.widget, c.STREAM_HEIGHT, 6, 2, command=int, allow_negative=True, allow_zero=True, default_value=240),
            self.getDisableButton(7, 0)
        ))

    def enableCoordinates(self):
        self.conditionalDisabling(
            self.widgets_dict[c.ROBOT_STREAM],
            (1,),
            (self.widgets_dict[c.STREAM_X], self.widgets_dict[c.STREAM_Y], self.widgets_dict[c.STREAM_WIDTH], self.widgets_dict[c.STREAM_HEIGHT])
        )

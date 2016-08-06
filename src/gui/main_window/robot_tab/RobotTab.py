from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
from gui_elements.widgets.frames import Frame
from gui_elements.widgets import Buttons, OptionMenu, Checkbutton, Textboxes
import constants as c


class RobotTab(DisableDeleteNotebookTab.Disable):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.ROBOT_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionMenu.TargetChoosingMenu(self, c.ROBOT_OPTION_FORWARD, 0, 1, (c.ROBOT_NONE,)),
            OptionMenu.TargetChoosingMenu(self, c.ROBOT_OPTION_BACKWARD, 1, 1, (c.ROBOT_NONE,)),
            OptionMenu.TargetChoosingMenu(self, c.ROBOT_OPTION_RIGHT, 2, 1, (c.ROBOT_NONE,)),
            OptionMenu.TargetChoosingMenu(self, c.ROBOT_OPTION_LEFT, 3, 1, (c.ROBOT_NONE,)),
            OptionMenu.TargetChoosingMenu(self, c.ROBOT_OPTION_STOP, 4, 1, (c.ROBOT_NONE,)),
            Buttons.Button(self, c.ROBOT_TEST, 0, 3, command=self.forwardClicked),
            Buttons.Button(self, c.ROBOT_TEST, 1, 3, command=self.backwardClicked),
            Buttons.Button(self, c.ROBOT_TEST, 2, 3, command=self.rightClicked),
            Buttons.Button(self, c.ROBOT_TEST, 3, 3, command=self.leftClicked),
            Buttons.Button(self, c.ROBOT_TEST, 4, 3, command=self.stopClicked),
            Textboxes.LabelTextbox(self, c.STREAM_X, 5, 0, command=int, allow_negative=True, allow_zero=True),
            Textboxes.LabelTextbox(self, c.STREAM_Y, 5, 2, command=int, allow_negative=True, allow_zero=True),
            Checkbutton.Checkbutton(self, c.ROBOT_STREAM, 5, 4, command=self.enableCoordinates, default_value=1),
            Textboxes.LabelTextbox(self, c.STREAM_WIDTH, 6, 0, command=int, allow_negative=True, allow_zero=True, default_value=320),
            Textboxes.LabelTextbox(self, c.STREAM_HEIGHT, 6, 2, command=int, allow_negative=True, allow_zero=True, default_value=240),
            self.getDisableButton(7, 0)
        ))

    def forwardClicked(self):
        self.sendEventToRoot(lambda x: x.robotForwardEvent())

    def backwardClicked(self):
        self.sendEventToRoot(lambda x: x.robotBackwardEvent())

    def leftClicked(self):
        self.sendEventToRoot(lambda x: x.robotLeftEvent())

    def rightClicked(self):
        self.sendEventToRoot(lambda x: x.robotRightEvent())

    def stopClicked(self):
        self.sendEventToRoot(lambda x: x.robotStopEvent())

    def enableCoordinates(self):
        self.conditionalDisabling(
            self.widgets_dict[c.ROBOT_STREAM],
            (1,),
            (self.widgets_dict[c.STREAM_X], self.widgets_dict[c.STREAM_Y], self.widgets_dict[c.STREAM_WIDTH], self.widgets_dict[c.STREAM_HEIGHT])
        )

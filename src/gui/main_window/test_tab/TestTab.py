from gui_elements.widgets.frames import Frame
from gui_elements.widgets import OptionMenu, Checkbutton, Textboxes
import constants as c


class TestTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_TEST_TAB, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self, c.TEST_TAB_EEG_SOURCE_OPTION_MENU, 0, 1, c.EEG_SOURCE_NAMES),
            Checkbutton.Checkbutton(self, c.TEST_TAB_ALLOW_REPEATING, 0, 3),
            OptionMenu.TargetChoosingMenu(self, c.TEST_TAB_TARGET, 1, 1, (c.TEST_TARGET_NONE, c.TEST_TARGET_RANDOM, c.TEST_TARGET_TIMED), columnspan=2),
            Checkbutton.Checkbutton(self, c.TEST_TAB_CLEAR_BUFFERS, 1, 3),
            OptionMenu.TargetChoosingMenu(self, c.TEST_TAB_STANDBY, 2, 1, (c.TEST_TARGET_NONE,), columnspan=2),
            Checkbutton.Checkbutton(self, c.TEST_TAB_PROCESS_SHORT_SIGNALS, 2, 3),
            Textboxes.LabelTextbox(self, c.TEST_TAB_TIME, 3, 0, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_TAB_UNLIMITED]),
            Checkbutton.Checkbutton(self, c.TEST_TAB_UNLIMITED, 3, 2, columnspan=2, command=self.enableTime, default_value=1),
            Textboxes.ColorTextboxFrame(self, c.TEST_TAB_COLOR, 4, 0, default_value="#ffffb3"),
        ))

    def enableTime(self):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_TAB_UNLIMITED],
            (0,),
            (self.widgets_dict[c.TEST_TAB_TIME],)
        )

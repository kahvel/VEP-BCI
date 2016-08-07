from gui_elements.widgets.frames import Frame
from gui_elements.widgets import OptionMenu, Checkbutton, Textboxes
import constants as c


class TestTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_TEST_TAB, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self, c.TEST_TAB_EEG_SOURCE_OPTION_MENU, 0, 1, c.EEG_SOURCE_NAMES),
            Textboxes.ColorTextboxFrame(self, c.TEST_COLOR, 0, 3, default_value="#ffffb3"),
            OptionMenu.TargetChoosingMenu(self, c.TEST_TARGET, 1, 1, (c.TEST_NONE, c.TEST_RANDOM, c.TEST_TIMED), columnspan=2),
            Checkbutton.Checkbutton(self, c.TEST_CLEAR_BUFFERS, 1, 3),
            OptionMenu.TargetChoosingMenu(self, c.TEST_STANDBY, 2, 1, (c.TEST_NONE,), columnspan=2),
            Checkbutton.Checkbutton(self, c.TEST_PROCESS_SHORT_SIGNALS, 2, 3),
            Textboxes.LabelTextbox(self, c.TEST_TIME, 3, 0, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_UNLIMITED]),
            Checkbutton.Checkbutton(self, c.TEST_UNLIMITED, 3, 2, columnspan=2, command=self.enableTime, default_value=1),
        ))

    def enableTime(self):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_UNLIMITED],
            (0,),
            (self.widgets_dict[c.TEST_TIME],)
        )

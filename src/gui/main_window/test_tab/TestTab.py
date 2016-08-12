from gui_elements.widgets.frames import Frame
from gui_elements.widgets import OptionMenu, Checkbutton, Textboxes
import constants as c


class TestTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_TEST_TAB, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.RecordingChoosingMenu(self, c.TEST_TAB_EEG_SOURCE_OPTION_MENU, 0, 1, c.EEG_SOURCE_NAMES),
            Checkbutton.Checkbutton(self, c.TEST_TAB_ALLOW_REPEATING, 0, 3),
            OptionMenu.TargetChoosingMenu(self, c.TEST_TAB_TARGET_OPTION_MENU, 1, 1, c.TEST_TARGET_OPTIONS, command=self.enableTimePerTarget, columnspan=2),
            Checkbutton.Checkbutton(self, c.TEST_TAB_CLEAR_BUFFERS, 1, 3),
            OptionMenu.TargetChoosingMenu(self, c.TEST_TAB_STANDBY, 2, 1, (c.TEST_TARGET_NONE,), columnspan=2),
            Checkbutton.Checkbutton(self, c.TEST_TAB_PROCESS_SHORT_SIGNALS, 2, 3),
            Textboxes.LabelTextbox(self, c.TEST_TAB_TOTAL_TIME, 3, 0, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_TAB_UNLIMITED]),
            Checkbutton.Checkbutton(self, c.TEST_TAB_UNLIMITED, 3, 2, columnspan=2, command=self.enableTotalTime, default_value=1),
            Textboxes.LabelTextbox(self, c.TEST_TAB_TIME_PER_TARGET, 4, 0, command=int, default_value=9, default_disability=True, default_disablers=[c.TEST_TAB_TARGET_OPTION_MENU]),
            Textboxes.LabelTextbox(self, c.TEST_TAB_TIME_PER_TARGET_PLUS_MINUS, 4, 2, command=int, allow_zero=True, default_value=2, default_disability=True, default_disablers=[c.TEST_TAB_TARGET_OPTION_MENU]),
            Textboxes.ColorTextboxFrame(self, c.TEST_TAB_COLOR, 5, 0, default_value="#ffffb3"),
        ))

    def enableTotalTime(self):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_TAB_UNLIMITED],
            (0,),
            (self.widgets_dict[c.TEST_TAB_TOTAL_TIME],)
        )

    def enableTimePerTarget(self, *dummy_arg_for_target_choosing_menu):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_TAB_TARGET_OPTION_MENU],
            (c.TEST_TARGET_TIMED, c.TEST_TARGET_RECORDING),
            (self.widgets_dict[c.TEST_TAB_TIME_PER_TARGET], self.widgets_dict[c.TEST_TAB_TIME_PER_TARGET_PLUS_MINUS])
        )

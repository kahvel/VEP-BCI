from gui_elements.widgets.frames import Frame
from gui_elements.widgets import OptionMenu, Checkbutton, Textboxes
import constants as c


class TestTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_TEST_TAB, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.RecordingChoosingMenu(self, c.TEST_TAB_EEG_SOURCE_OPTION_MENU, 0, 1, c.EEG_SOURCE_NAMES, command=self.eegSourceOptionMenuCommand),
            Checkbutton.Checkbutton(self, c.TEST_TAB_ALLOW_REPEATING, 0, 3),
            OptionMenu.OptionMenu(self, c.TEST_TAB_RECORDED_TYPE_OPTION_MENU, 1, 1, c.TEST_RECORDED_TYPE_NAMES, default_disability=True, default_disablers=[c.TEST_TAB_EEG_SOURCE_OPTION_MENU]),
            Checkbutton.Checkbutton(self, c.TEST_TAB_CLEAR_BUFFERS, 1, 3),
            OptionMenu.TargetChoosingMenu(self, c.TEST_TAB_TARGET_OPTION_MENU, 2, 1, c.TEST_TARGET_OPTIONS, command=self.enableTimePerTarget, columnspan=2),
            Checkbutton.Checkbutton(self, c.TEST_TAB_PROCESS_SHORT_SIGNALS, 2, 3),
            OptionMenu.TargetChoosingMenu(self, c.TEST_TAB_STANDBY, 3, 1, (c.TEST_TARGET_NONE,), columnspan=2),
            Textboxes.LabelTextbox(self, c.TEST_TAB_TOTAL_TIME, 4, 0, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_TAB_UNLIMITED]),
            Checkbutton.Checkbutton(self, c.TEST_TAB_UNLIMITED, 4, 2, columnspan=2, command=self.enableTotalTime, default_value=1),
            Textboxes.LabelTextbox(self, c.TEST_TAB_TIME_PER_TARGET, 5, 0, command=float, default_value=9, default_disability=True, default_disablers=[c.TEST_TAB_TARGET_OPTION_MENU]),
            Textboxes.LabelTextbox(self, c.TEST_TAB_TIME_PER_TARGET_PLUS_MINUS, 5, 2, command=int, allow_zero=True, default_value=2, default_disability=True, default_disablers=[c.TEST_TAB_TARGET_OPTION_MENU]),
            Textboxes.ColorTextboxFrame(self, c.TEST_TAB_COLOR, 6, 0, default_value="#ffffb3"),
        ))

    def enableTotalTime(self):
        self.conditionalEnabling(
            self.widgets_dict[c.TEST_TAB_UNLIMITED],
            (0,),
            (self.widgets_dict[c.TEST_TAB_TOTAL_TIME],)
        )

    def enableTimePerTarget(self, dummy_arg_for_option_menu_command):
        self.conditionalEnabling(
            self.widgets_dict[c.TEST_TAB_TARGET_OPTION_MENU],
            (c.TEST_TARGET_TIMED, c.TEST_TARGET_RECORDING),
            (self.widgets_dict[c.TEST_TAB_TIME_PER_TARGET], self.widgets_dict[c.TEST_TAB_TIME_PER_TARGET_PLUS_MINUS])
        )

    def eegSourceOptionMenuCommand(self, dummy_arg_for_option_menu_command):
        self.enableTestTarget()
        self.disableRecordedType()

    def enableTestTarget(self):
        self.conditionalEnabling(
            self.widgets_dict[c.TEST_TAB_EEG_SOURCE_OPTION_MENU],
            (c.EEG_SOURCE_DEVICE,),
            (self.widgets_dict[c.TEST_TAB_TARGET_OPTION_MENU],)
        )

    def disableRecordedType(self):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_TAB_EEG_SOURCE_OPTION_MENU],
            (c.EEG_SOURCE_DEVICE,),
            (self.widgets_dict[c.TEST_TAB_RECORDED_TYPE_OPTION_MENU],)
        )

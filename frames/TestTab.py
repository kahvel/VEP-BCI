__author__ = 'Anti'

from widgets import Textboxes, Checkbutton, OptionMenu
from frames import Frame
import Tkinter
import constants as c


class TestTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.TEST_TAB, row, column, **kwargs)
        self.target_count = 0
        self.addChildWidgets((
            OptionMenu.OptionMenu  (self.widget, c.TEST_TARGET,    0, 1, columnspan=2, values=(c.TEST_NONE, c.TEST_RANDOM), command=self.enableRange),
            Checkbutton.Checkbutton(self.widget, c.TEST_STANDBY,   1, 0, columnspan=2),
            Checkbutton.Checkbutton(self.widget, c.TEST_UNLIMITED, 1, 2, columnspan=2, command=self.enableTime, default_value=1),
            Textboxes.LabelTextbox (self.widget, c.TEST_TIME,      2, 0, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_UNLIMITED]),
            Textboxes.LabelTextbox (self.widget, c.TEST_MIN,       2, 2, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_TARGET]),
            Textboxes.LabelTextbox (self.widget, c.TEST_MAX,       2, 4, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_TARGET])
        ))

    def enableTime(self):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_UNLIMITED],
            (0,),
            (self.widgets_dict[c.TEST_TIME],)
        )

    def enableRange(self):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_TARGET],
            (c.TEST_RANDOM,),
            (self.widgets_dict[c.TEST_MIN], self.widgets_dict[c.TEST_MAX])
        )

    def addOption(self, option):
        variable = self.widgets_dict[c.TEST_TARGET].variable
        self.widgets_dict[c.TEST_TARGET].widget["menu"].add_command(label=option, command=Tkinter._setit(variable, option))

    def targetAdded(self):
        self.target_count += 1
        self.addOption(self.target_count)

    def targetRemoved(self):
        self.widgets_dict[c.TEST_TARGET].widget["menu"].delete(0, Tkinter.END)
        self.addOption(c.TEST_NONE)
        self.addOption(c.TEST_RANDOM)
        self.target_count -= 1
        for i in range(1, self.target_count+1):
            self.addOption(i)
        if self.widgets_dict[c.TEST_TARGET].variable.get() > self.target_count:
            print("Warning: Test target in Test tab reset to None")
            self.widgets_dict[c.TEST_TARGET].variable.set(c.TEST_NONE)
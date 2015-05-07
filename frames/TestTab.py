__author__ = 'Anti'

from widgets import Textboxes, Checkbutton, OptionMenu, Buttons
from frames import Frame
import Tkinter
import constants as c


class ResultsFrame(Frame.Frame):
    def __init__(self, parent, buttons, row, column, **kwargs):
        show, reset, save = buttons
        Frame.Frame.__init__(self, parent, c.RESULT_FRAME, row, column, **kwargs)
        Tkinter.Label(self.widget, text="Results").grid(row=0, column=0, padx=5, pady=5)
        self.addChildWidgets((
            Buttons.Button(self.widget, c.RESULT_SHOW_BUTTON,  0, 1, command=show),
            Buttons.Button(self.widget, c.RESULT_RESET_BUTTON, 0, 2, command=reset),
            Buttons.Button(self.widget, c.RESULT_SAVE_BUTTON, 0, 3, command=save)
        ))


class TestTab(Frame.Frame):
    def __init__(self, parent, buttons, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.TEST_TAB, row, column, **kwargs)
        self.target_count = 0
        self.addChildWidgets((
            OptionMenu.OptionMenu  (self.widget, c.TEST_TARGET,    0, 1, columnspan=2, values=(c.TEST_NONE, c.TEST_RANDOM), command=self.enableRange),
            Textboxes.ColorTextboxFrame(self.widget, c.TEST_COLOR, c.TEST_COLOR_FRAME, 0, 3, default_value="#ffffb3"),
            OptionMenu.OptionMenu  (self.widget, c.TEST_STANDBY,   1, 1, columnspan=2, values=(c.TEST_NONE,)),
            Textboxes.LabelTextbox (self.widget, c.TEST_TIME,      2, 0, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_UNLIMITED]),
            Checkbutton.Checkbutton(self.widget, c.TEST_UNLIMITED, 2, 2, columnspan=2, command=self.enableTime, default_value=1),
            Textboxes.LabelTextbox (self.widget, c.TEST_MIN,       3, 0, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_TARGET]),
            Textboxes.LabelTextbox (self.widget, c.TEST_MAX,       3, 2, command=int, default_value=1, default_disability=True, default_disablers=[c.TEST_TARGET]),
            ResultsFrame(self.widget, buttons, 4, 0, columnspan=4)
        ))

    def enableTime(self):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_UNLIMITED],
            (0,),
            (self.widgets_dict[c.TEST_TIME],)
        )

    def enableRange(self, x=None):
        self.conditionalDisabling(
            self.widgets_dict[c.TEST_TARGET],
            (c.TEST_RANDOM,),
            (self.widgets_dict[c.TEST_MIN], self.widgets_dict[c.TEST_MAX])
        )

    def addOption(self, option, option_menu, command=lambda x: None):
        variable = option_menu.variable
        option_menu.widget["menu"].add_command(label=option, command=Tkinter._setit(variable, option, callback=command))

    def targetAdded(self):
        self.target_count += 1
        self.addOption(self.target_count, self.getTestMenu(), self.enableRange)
        self.addOption(self.target_count, self.getStandbyMenu())

    def deleteOptions(self, option_menu):
        option_menu.widget["menu"].delete(0, Tkinter.END)

    def getTestMenu(self):
        return self.widgets_dict[c.TEST_TARGET]

    def getTestTarget(self):
        return self.getTestMenu().variable.get()

    def setTestTarget(self, value):
        self.getTestMenu().variable.set(value)

    def getStandbyMenu(self):
        return self.widgets_dict[c.TEST_STANDBY]

    def getStandbyTarget(self):
        return self.getStandbyMenu().variable.get()

    def setStandbyTarget(self, value):
        self.getStandbyMenu().variable.set(value)

    def updateOptionMenu(self, deleted_tab, target, setValue):
        deleted_tab += 1
        if target != c.TEST_NONE and target != c.TEST_RANDOM:
            target = int(target)
            if target == deleted_tab:
                print("Warning: OptionMenu in Test tab reset to None")
                setValue(c.TEST_NONE)
            elif target > deleted_tab:
                setValue(target-1)

    def targetRemoved(self, deleted_tab):
        self.deleteOptions(self.getTestMenu())
        self.deleteOptions(self.getStandbyMenu())
        self.addOption(c.TEST_NONE, self.getTestMenu(), self.enableRange)
        self.addOption(c.TEST_RANDOM, self.getTestMenu(), self.enableRange)
        self.addOption(c.TEST_NONE, self.getStandbyMenu())
        self.target_count -= 1
        for i in range(1, self.target_count+1):
            self.addOption(i, self.getTestMenu(), self.enableRange)
            self.addOption(i, self.getStandbyMenu())
        self.updateOptionMenu(deleted_tab, self.getTestTarget(), self.setTestTarget)
        self.updateOptionMenu(deleted_tab, self.getStandbyTarget(), self.setStandbyTarget)

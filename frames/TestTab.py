__author__ = 'Anti'

from widgets import Textboxes, Checkbutton, OptionMenu
from frames import Frame
import Tkinter


class TestTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, "Test", row, column, **kwargs)
        self.target_count = 0
        self.addChildWidgets((
            Textboxes.LabelTextbox (self.widget, "Time",        0, 0, command=int, default_value=1),
            Textboxes.LabelTextbox (self.widget, "Min",         0, 2, command=int, default_value=1, default_disability=True, default_disablers=["Test target"]),
            Textboxes.LabelTextbox (self.widget, "Max",         0, 4, command=int, default_value=1, default_disability=True, default_disablers=["Test target"]),
            Checkbutton.Checkbutton(self.widget, "Standby",     1, 2, columnspan=2),
            OptionMenu.OptionMenu  (self.widget, "Test target", 1, 0, columnspan=2, values=("None", "Random"), command=self.disableRange),
            Checkbutton.Checkbutton(self.widget, "Unlimited",   1, 4, columnspan=2, command=self.disableTime)
        ))

    def disableTime(self):
        self.conditionalDisabling(
            self.widgets_dict["Unlimited"],
            0,
            (self.widgets_dict["Time"],)
        )

    def disableRange(self):
        self.conditionalDisabling(
            self.widgets_dict["Test target"],
            "Random",
            (
                self.widgets_dict["Min"],
                self.widgets_dict["Max"]
            )
        )

    def addOption(self, option):
        variable = self.widgets_dict["Test target"].variable
        self.widgets_dict["Test target"].widget["menu"].add_command(label=option, command=Tkinter._setit(variable, option))

    def targetAdded(self):
        self.target_count += 1
        self.addOption(self.target_count)

    def targetRemoved(self):
        self.widgets_dict["Test target"].widget["menu"].delete(0, Tkinter.END)
        self.addOption("None")
        self.addOption("Random")
        self.target_count -= 1
        for i in range(1, self.target_count+1):
            self.addOption(i)
        if self.widgets_dict["Test target"].variable.get() > self.target_count:
            print("Warning: OptionMenu in tab Test reset to None")
            self.widgets_dict["Test target"].variable.set("None")

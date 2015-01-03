__author__ = 'Anti'

from widgets import Textboxes, OptionMenu, Buttons, Frame
import win32api
import win32con
import Tkinter


class WindowTab(Frame.Frame):
    def __init__(self, row, column, columnspan, padx, pady, change_target_freqs):
        Frame.Frame.__init__(self, "WindowTab", row, column, columnspan, padx, pady)
        self.change_target_freqs = change_target_freqs

        monitor_names = self.getMonitorNames()
        monitor_command = lambda: self.updateMonitorFreqTextbox(self.widgets_dict["Monitor"].widget, self.widgets_dict["Monitor"].variable, self.widgets_dict["Freq"])
        refresh_command = lambda:      self.refreshMonitorNames(self.widgets_dict["Monitor"].widget, self.widgets_dict["Monitor"].variable, self.widgets_dict["Freq"])

        self.addChildWidgets((
            Textboxes.LabelTextbox("Width",   0, 0, int,   False, False, default_value=800),
            Textboxes.LabelTextbox("Height",  0, 2, int,   False, False, default_value=600),
            Textboxes.ColorTextbox("Color",   0, 4,                      default_value="#000000"),
            OptionMenu.OptionMenu ("Monitor", 1, 0, monitor_command, monitor_names),
            Textboxes.LabelTextbox("Freq",    1, 2, float, False, False, default_value=self.getMonitorFrequency(monitor_names[0])),
            Buttons.Button        ("Refresh", 1, 4, refresh_command)
        ))

    def getMonitorNames(self):
        return [win32api.GetMonitorInfo(monitor[0])["Device"] for monitor in win32api.EnumDisplayMonitors()]

    def getMonitorFrequency(self, monitor_name):
        return getattr(win32api.EnumDisplaySettings(monitor_name, win32con.ENUM_CURRENT_SETTINGS), "DisplayFrequency")

    def refreshMonitorNames(self, widget, var, textbox):
        widget["menu"].delete(0, Tkinter.END)
        for monitor_name in self.getMonitorNames():
            widget["menu"].add_command(label=monitor_name, command=lambda x=monitor_name: (var.set(x), self.updateMonitorFreqTextbox(widget, var, textbox)))
        self.updateMonitorFreqTextbox(widget, var, textbox)
        textbox.validate()

    def updateMonitorFreqTextbox(self, widget, var, textbox):
        monitor_names = self.getMonitorNames()
        if var.get() not in monitor_names:
            var.set(monitor_names[0])
            self.refreshMonitorNames(widget, var, textbox)
        else:
            textbox.updateValue(self.getMonitorFrequency(var.get()))
        self.change_target_freqs()
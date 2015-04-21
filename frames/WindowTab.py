__author__ = 'Anti'

from widgets import Textboxes, OptionMenu, Buttons
from frames import Frame
import win32api
import win32con
import Tkinter
import constants as c


class WindowTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.WINDOW_TAB, row, column, **kwargs)
        self.change_target_freqs = kwargs["change_target_freqs"]

        monitor_names = self.getMonitorNames()
        monitor_command = lambda: self.updateMonitorFreqTextbox(self.widgets_dict[c.WINDOW_MONITOR].widget, self.widgets_dict[c.WINDOW_MONITOR].variable, self.widgets_dict[c.WINDOW_FREQ])
        refresh_command = lambda:      self.refreshMonitorNames(self.widgets_dict[c.WINDOW_MONITOR].widget, self.widgets_dict[c.WINDOW_MONITOR].variable, self.widgets_dict[c.WINDOW_FREQ])

        self.addChildWidgets((
            Textboxes.LabelTextbox     (self.widget, c.WINDOW_WIDTH,   0, 0, command=int,   default_value=800),
            Textboxes.LabelTextbox     (self.widget, c.WINDOW_HEIGHT,  0, 2, command=int,   default_value=600),
            Textboxes.ColorTextboxFrame(self.widget, c.WINDOW_COLOR, c.WINDOW_COLOR_FRAME,   0, 4,                default_value="#000000"),
            Textboxes.LabelTextbox     (self.widget, c.WINDOW_FREQ,    1, 0, command=float, default_value=self.getMonitorFrequency(monitor_names[0])),
            Buttons.Button             (self.widget, c.WINDOW_REFRESH, 1, 2, command=refresh_command),
            OptionMenu.OptionMenu      (self.widget, c.WINDOW_MONITOR, 2, 1, command=monitor_command, values=monitor_names, columnspan=3)
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

    def updateMonitorFreqTextbox(self, widget, var, textbox):
        monitor_names = self.getMonitorNames()
        if var.get() not in monitor_names:
            var.set(monitor_names[0])
            self.refreshMonitorNames(widget, var, textbox)
        else:
            textbox.setValue(self.getMonitorFrequency(var.get()))
            textbox.validate()
        self.change_target_freqs()
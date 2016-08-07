import win32api
import Tkinter

import win32con

from gui_elements.widgets import OptionMenu, Buttons, Textboxes
from gui_elements.widgets.frames import Frame
from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
import TargetsNotebook
import constants as c


class MonitorFrame(DisableDeleteNotebookTab.Disable):
    def __init__(self, parent, **kwargs):
        DisableDeleteNotebookTab.Disable.__init__(self, parent, c.WINDOW_TAB_MONITOR_FRAME, **kwargs)
        self.loading_default_value = True
        monitor_names = self.getMonitorNames()
        monitor_command = lambda: self.updateMonitorFreqTextbox(self.widgets_dict[c.WINDOW_MONITOR].widget, self.widgets_dict[c.WINDOW_MONITOR].variable, self.widgets_dict[c.WINDOW_FREQ])
        refresh_command = lambda:      self.refreshMonitorNames(self.widgets_dict[c.WINDOW_MONITOR].widget, self.widgets_dict[c.WINDOW_MONITOR].variable, self.widgets_dict[c.WINDOW_FREQ])
        self.addChildWidgets((
            Textboxes.LabelTextbox     (self, c.WINDOW_WIDTH,   0, 0, command=int,   default_value=800),
            Textboxes.LabelTextbox     (self, c.WINDOW_HEIGHT,  0, 2, command=int,   default_value=600),
            Textboxes.ColorTextboxFrame(self, c.WINDOW_COLOR,   0, 4,                default_value="#000000"),
            Textboxes.LabelTextbox     (self, c.WINDOW_FREQ,    1, 0, command=self.monitorFrequencyTextboxCommand, default_value=self.getMonitorFrequency(monitor_names[0])),
            Buttons.Button             (self, c.WINDOW_REFRESH, 1, 2, command=refresh_command),
            OptionMenu.OptionMenu      (self, c.WINDOW_MONITOR, 2, 1, monitor_names, command=monitor_command, columnspan=3),
            self.getDisableButton(2, 4),
        ))

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

    def getMonitorNames(self):
        return [win32api.GetMonitorInfo(monitor[0])["Device"] for monitor in win32api.EnumDisplayMonitors()]

    def getMonitorFrequency(self, monitor_name):
        return getattr(win32api.EnumDisplaySettings(monitor_name, win32con.ENUM_CURRENT_SETTINGS), "DisplayFrequency")

    def monitorFrequencyTextboxCommand(self, value):
        float(value)
        if not self.loading_default_value:
            self.sendEventToRoot(lambda x: x.monitorFrequencyChangedEvent())
        else:
            self.loading_default_value = False


class TargetsTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_TARGETS_TAB, row, column, **kwargs)
        self.addChildWidgets((
            MonitorFrame(self),
            TargetsNotebook.TargetsNotebook(self, 1, 0, self.getMonitorFreq),
        ))

    def getMonitorFreq(self):
        return float(self.widgets_dict[c.WINDOW_TAB_MONITOR_FRAME].widgets_dict[c.WINDOW_FREQ].getValue())

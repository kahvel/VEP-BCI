__author__ = 'Anti'

import ttk
import math
from frames import WindowTab, TestTab, RecordTab, ResultsTab, Frame
import SameTabsNotebook


class MainNotebook(Frame.AbstractFrame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.AbstractFrame.__init__(self, parent, "MainNotebook", row, column, **kwargs)
        validate_freq = lambda textbox, d: self.changeFreq(self.widgets_dict["Window"].widgets_dict["Freq"], textbox, d)
        monitor_freq_changed = lambda: self.changeAllFreqs(self.widgets_dict["Window"].widgets_dict["Freq"], self.widgets_dict["Targets"])
        self.create(ttk.Notebook(parent))
        self.test_tab = TestTab.TestTab(self.widget, 0, 0)
        self.addChildWidgets((
            WindowTab.WindowTab(self.widget, 0, 0, change_target_freqs=monitor_freq_changed),
            SameTabsNotebook.TargetNotebook(self.widget, 0, 0, self.targetAdded, self.targetRemoved, validate_freq=validate_freq),
            SameTabsNotebook.ExtractionNotebook(self.widget, 0, 0),
            SameTabsNotebook.PlotNotebook(self.widget, 0, 0),
            self.test_tab,
            RecordTab.RecordTab(self.widget, 0, 0),
            ResultsTab.ResultsTab(self.widget, 0, 0)
        ))
        self.createChildWidgets()

    def createChildWidgets(self):
        for widget in self.widgets_list:
            self.widget.add(widget.widget, text=widget.name)

    def changeAllFreqs(self, monitor_freq_textbox, widget):  # Recursively search for widgets named Freq
        if widget.name == "Freq":
            if widget.validate():
                self.changeFreq(monitor_freq_textbox, widget)
        elif isinstance(widget, Frame.Frame):
            for child_widget in widget.widgets_list:
                self.changeAllFreqs(monitor_freq_textbox, child_widget)

    def changeFreq(self, monitor_freq_textbox, target_freq_textbox, d=0):
        target_freq = float(target_freq_textbox.widget.get())
        monitor_freq = int(monitor_freq_textbox.widget.get())
        freq_on = math.floor(monitor_freq/target_freq/2)
        freq_off = math.ceil(monitor_freq/target_freq/2)
        if freq_off+freq_on+d != 0:
            target_freq_textbox.setValue(float(monitor_freq)/(freq_off+freq_on+d))
            return True
        else:
            return False

    def targetAdded(self):
        self.test_tab.targetAdded()

    def targetRemoved(self):
        self.test_tab.targetRemoved()

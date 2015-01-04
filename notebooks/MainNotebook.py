__author__ = 'Anti'

import ttk
import math

from frames import WindowTab, TestTab, RecordTab, ResultsTab, Frame
import SameTabsNotebook


class MainNotebook(Frame.Frame):
    def __init__(self, row, column, columnspan, padx, pady):
        Frame.Frame.__init__(self, "MainNotebook", row, column, columnspan, padx, pady)
        validate_freq = lambda textbox, d: self.changeFreq(self.widgets_dict["Window"].widgets_dict["Freq"], textbox, d)
        monitor_freq_changed = lambda: self.changeAllFreqs(self.widgets_dict["Window"].widgets_dict["Freq"], self.widgets_dict["Targets"])
        self.addChildWidgets((
            WindowTab.WindowTab(0, 0, 1, 0, 0, monitor_freq_changed),
            SameTabsNotebook.TargetNotebook(0, 0, 1, 0, 0, validate_freq),
            SameTabsNotebook.ExtractionNotebook(0, 0, 1, 0, 0),
            SameTabsNotebook.PlotNotebook(0, 0, 1, 0, 0),
            TestTab.TestTab(0, 0, 1, 0, 0),
            RecordTab.RecordTab(0, 0, 1, 0, 0),
            ResultsTab.ResultsTab(0, 0, 1, 0, 0)
        ))

    def createWidget(self, parent):
        widget = ttk.Notebook(parent)
        self.createChildWidgets(widget)
        return widget

    def createChildWidgets(self, notebook):
        Frame.Frame.createChildWidgets(self, notebook)
        for widget in self.widgets_list:
            notebook.add(widget.widget, text=widget.name)

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
            target_freq_textbox.updateValue(float(monitor_freq)/(freq_off+freq_on+d))

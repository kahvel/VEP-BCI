__author__ = 'Anti'

import PlotExtractionNotebook
from main_window import MyWindows
from main_logic import SignalPlot, FFTPlot


class PlotNotebook(PlotExtractionNotebook.PlotExtractionNotebook):
    def __init__(self, parent):
        PlotExtractionNotebook.PlotExtractionNotebook.__init__(self, parent)

    def addListElement(self):
        PlotExtractionNotebook.PlotExtractionNotebook.addListElement(self)
        self.classes.append({"Signal": {}, "PS": {}})

    def buttonFrame(self, frame, classes, buttons):
        MyWindows.initButtonFrame(frame, ["Signal", "Sum signal", "Avg signal", "Sum avg signal", "Power", "Sum power", "Avg power", "Sum avg power"],
                                  [lambda: self.createInstance(SignalPlot, classes["Signal"], "MultipleRegular"),
                                   lambda: self.createInstance(SignalPlot, classes["Signal"], "SingleRegular"),
                                   lambda: self.createInstance(SignalPlot, classes["Signal"], "MultipleAverage"),
                                   lambda: self.createInstance(SignalPlot, classes["Signal"], "SingleAverage"),
                                   lambda: self.createInstance(FFTPlot, classes["PS"], "MultipleRegular"),
                                   lambda: self.createInstance(FFTPlot, classes["PS"], "SingleRegular"),
                                   lambda: self.createInstance(FFTPlot, classes["PS"], "MultipleAverage"),
                                   lambda: self.createInstance(FFTPlot, classes["PS"], "SingleAverage")],
                                  start_row=1, buttons=buttons, buttons_in_row=4)
__author__ = 'Anti'

import PlotExtractionNotebook
from main_window import MyWindows
from main_logic import SignalPlot, FFTPlot


class PlotNotebook(PlotExtractionNotebook.PlotExtractionNotebook):
    def __init__(self, parent):
        PlotExtractionNotebook.PlotExtractionNotebook.__init__(self, parent)

    def addListElement(self):
        PlotExtractionNotebook.PlotExtractionNotebook.addListElement(self)
        self.windows.append({"Signal": {}, "Power": {}})

    def buttonFrame(self, frame, windows, buttons):
        MyWindows.initButtonFrame(frame, ["Signal", "Sum signal", "Avg signal", "Sum avg signal", "Power", "Sum power", "Avg power", "Sum avg power"],
                                  [lambda: self.createWindow(SignalPlot, windows["Signal"], "MultipleRegular"),
                                   lambda: self.createWindow(SignalPlot, windows["Signal"], "SingleRegular"),
                                   lambda: self.createWindow(SignalPlot, windows["Signal"], "MultipleAverage"),
                                   lambda: self.createWindow(SignalPlot, windows["Signal"], "SingleAverage"),
                                   lambda: self.createWindow(FFTPlot, windows["Power"], "MultipleRegular"),
                                   lambda: self.createWindow(FFTPlot, windows["Power"], "SingleRegular"),
                                   lambda: self.createWindow(FFTPlot, windows["Power"], "MultipleAverage"),
                                   lambda: self.createWindow(FFTPlot, windows["Power"], "SingleAverage")],
                                  start_row=1, buttons=buttons, buttons_in_row=4)

    def frameGenerator(self, parent, remove, disable):
        frame = PlotExtractionNotebook.PlotExtractionNotebook.frameGenerator(self, parent, remove, disable)
        windows, buttons = self.windows[-1], self.buttons[-1]
        MyWindows.initButtonFrame(frame, ["Reset avg signal", "Reset sum avg signal", "Reset avg power", "Reset sum avg power"],
                                  [lambda: self.resetWindow(windows["Signal"], "MultipleAverage"),
                                   lambda: self.resetWindow(windows["Signal"], "SingleAverage"),
                                   lambda: self.resetWindow(windows["Power"], "MultipleAverage"),
                                   lambda: self.resetWindow(windows["Power"], "SingleAverage")],
                                  start_row=4, buttons=buttons, buttons_in_row=2, columnspan=2)
        return frame

    def resetWindow(self, windows, key):
        if key in windows:
            windows[key].reset()
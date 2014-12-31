__author__ = 'Anti'

import Tkinter
import PlotExtractionNotebook
from main_window import MyWindows
from main_logic import PSDAExtraction, CCAExtraction, CCAPSDAExtraction


class ExctractionNotebook(PlotExtractionNotebook.PlotExtractionNotebook):
    def __init__(self, parent):
        PlotExtractionNotebook.PlotExtractionNotebook.__init__(self, parent)

    def addListElement(self):
        PlotExtractionNotebook.PlotExtractionNotebook.addListElement(self)
        self.windows.append({"PSDA": {}, "CCA": {}, "Both": {}})

    def buttonFrame(self, frame, windows, buttons):
        MyWindows.initButtonFrame(frame, ["PSDA", "Sum PSDA", "CCA", "Both", "Sum Both"],
                                  [lambda: self.createWindow(PSDAExtraction, windows["PSDA"], "Multiple"),
                                   lambda: self.createWindow(PSDAExtraction, windows["PSDA"], "Single"),
                                   lambda: self.createWindow(CCAExtraction, windows["CCA"], "Single"),
                                   lambda: self.createWindow(CCAPSDAExtraction, windows["Both"], "Multiple"),
                                   lambda: self.createWindow(CCAPSDAExtraction, windows["Both"], "Single")],
                                  start_row=1, buttons=buttons)

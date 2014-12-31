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
        self.classes.append({"PSDA": {}, "CCA": {}, "Both": {}})

    def buttonFrame(self, frame, classes, buttons):
        MyWindows.initButtonFrame(frame, ["PSDA", "Sum PSDA", "CCA", "Both", "Sum Both"],
                                  [lambda: self.createInstance(PSDAExtraction, classes["PSDA"], "Multiple"),
                                   lambda: self.createInstance(PSDAExtraction, classes["PSDA"], "Single"),
                                   lambda: self.createInstance(CCAExtraction, classes["CCA"], "Single"),
                                   lambda: self.createInstance(CCAPSDAExtraction, classes["Both"], "Multiple"),
                                   lambda: self.createInstance(CCAPSDAExtraction, classes["Both"], "Single")],
                                  start_row=1, buttons=buttons)

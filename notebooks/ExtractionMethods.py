__author__ = 'Anti'

from frames import ExtractionMethodTab
from notebooks import Notebook
import constants as c


class ExtractionMethods(Notebook.Notebook):
    def __init__(self, parent, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.EXTRACTION_NOTEBOOK, row, column, **kwargs)
        self.addChildWidgets((
            ExtractionMethodTab.PsdaExtraction(self.widget, **kwargs),
            ExtractionMethodTab.CcaExtraction(self.widget, **kwargs)
        ))

    def createChildWidgets(self):
        for widget in self.widgets_list:
            self.widget.add(widget.widget, text=widget.name)

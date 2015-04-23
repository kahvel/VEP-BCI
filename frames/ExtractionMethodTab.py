__author__ = 'Anti'

from frames import DisableDeleteNotebookTab, OptionsFrame
import constants as c


class ExtractionMethodTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, name, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, name, **kwargs)
        self.addChildWidgets((
            OptionsFrame.SensorsFrame(self.widget, 0, 0, **kwargs),
            OptionsFrame.OptionsFrame(self.widget, 1, 0, **kwargs),
            self.getDisableDeleteFrame(2, 0, **kwargs)
        ))


class PsdaExtraction(ExtractionMethodTab):
    def __init__(self, parent, **kwargs):
        ExtractionMethodTab.__init__(self, parent, c.PSDA_METHOD_TAB, **kwargs)


class CcaExtraction(ExtractionMethodTab):
    def __init__(self, parent, **kwargs):
        ExtractionMethodTab.__init__(self, parent, c.CCA_METHOD_TAB, **kwargs)


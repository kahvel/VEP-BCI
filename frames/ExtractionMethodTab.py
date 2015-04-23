__author__ = 'Anti'

from frames import OptionsFrame, DisableDeleteNotebookTab
import constants as c


class ExtractionMethodTab(DisableDeleteNotebookTab.Disable):
    def __init__(self, parent, name, **kwargs):
        DisableDeleteNotebookTab.Disable.__init__(self, parent, name, **kwargs)


class PsdaExtraction(ExtractionMethodTab):
    def __init__(self, parent, **kwargs):
        ExtractionMethodTab.__init__(self, parent, c.PSDA_METHOD_TAB, **kwargs)
        self.addChildWidgets((
            OptionsFrame.SensorsFrame(self.widget, 0, 0, **kwargs),
            OptionsFrame.PsdaOptionsFrame(self.widget, 1, 0, **kwargs),
            self.getDisableButton(2, 0, **kwargs)
        ))


class CcaExtraction(ExtractionMethodTab):
    def __init__(self, parent, **kwargs):
        ExtractionMethodTab.__init__(self, parent, c.CCA_METHOD_TAB, **kwargs)
        self.addChildWidgets((
            OptionsFrame.SensorsFrame(self.widget, 0, 0, **kwargs),
            OptionsFrame.CcaOptionsFrame(self.widget, 1, 0, **kwargs),
            self.getDisableButton(2, 0, **kwargs)
        ))

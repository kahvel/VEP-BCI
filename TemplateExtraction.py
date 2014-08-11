__author__ = 'Anti'

import ExtractionWindow
import Signal


class TemplateExtraction(ExtractionWindow.ExtractionWindow, Signal.Multiple):
    def __init__(self):
        ExtractionWindow.ExtractionWindow.__init__(self, "Template Extraction")
        Signal.Multiple.__init__(self)

    def getGenerator(self):
        return Signal.Regular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()

    def generator(self, index, start_deleting):
        pass # TODO implement this
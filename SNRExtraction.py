__author__ = 'Anti'

import ExtractionWindow
import FFT


class SumSNR(ExtractionWindow.ExtractionWindow, FFT.SingleRegular):
    def __init__(self):
        ExtractionWindow.ExtractionWindow.__init__(self, "Sum SNR")
        FFT.SingleRegular.__init__(self)


class SNR(ExtractionWindow.ExtractionWindow, FFT.MultipleRegular):
    def __init__(self):
        ExtractionWindow.ExtractionWindow.__init__(self, "SNR")
        FFT.MultipleRegular.__init__(self)
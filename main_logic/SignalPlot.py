__author__ = 'Anti'

from controllable_windows import PlotWindow
from signal_processing import Signal
from main_logic import Abstract


class SignalPlot(PlotWindow.PlotWindow):
    def __init__(self, title):
        PlotWindow.PlotWindow.__init__(self, title)

    def getScale(self):
        return 10, -10


class MultipleRegular(Abstract.Multiple, SignalPlot):
    def __init__(self):
        Abstract.Multiple.__init__(self)
        SignalPlot.__init__(self, "Signals")

    def getCoordGenerator(self):
        return Signal.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class SingleRegular(Abstract.Single, SignalPlot):
    def __init__(self):
        Abstract.Single.__init__(self)
        SignalPlot.__init__(self, "Sum of signals")

    def getCoordGenerator(self):
        return Signal.SingleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class MultipleAverage(Abstract.Multiple, SignalPlot):
    def __init__(self):
        SignalPlot.__init__(self, "Average signals")

    def getCoordGenerator(self):
        return Signal.MultipleAverage(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class SingleAverage(Abstract.Single, SignalPlot):
    def __init__(self):
        Abstract.Single.__init__(self)
        SignalPlot.__init__(self, "Sum of average signals")

    def getCoordGenerator(self):
        return Signal.SingleAverage(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()
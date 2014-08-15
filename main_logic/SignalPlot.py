__author__ = 'Anti'

from controllable_windows import PlotWindow
from signal_processing import Signal
from main_logic import Abstract
import operator


class SignalPlot(PlotWindow.PlotWindow):
    def __init__(self, title):
        PlotWindow.PlotWindow.__init__(self, title)

    def startDeleting(self):
        return lambda packet_count: operator.ge(packet_count, self.options["Length"]-1)

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(packet_count-len(coordinates)+1, packet_count+1):
            result.append(i*self.window_width/self.options["Length"])
            result.append(self.scaleY(coordinates.popleft(),  index, self.plot_count, 10, -10))
        return result


class MultipleRegular(Abstract.Multiple, SignalPlot):
    def __init__(self):
        Abstract.Multiple.__init__(self)
        SignalPlot.__init__(self, "Signals")

    def getGenerator(self):
        return Signal.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class SingleRegular(Abstract.Single, SignalPlot):
    def __init__(self):
        Abstract.Single.__init__(self)
        SignalPlot.__init__(self, "Sum of signals")

    def getGenerator(self):
        return Signal.SingleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class MultipleAverage(Abstract.Multiple, SignalPlot):
    def __init__(self):
        SignalPlot.__init__(self, "Average signals")

    def getGenerator(self):
        return Signal.MultipleAverage(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class SingleAverage(Abstract.Single, SignalPlot):
    def __init__(self):
        Abstract.Single.__init__(self)
        SignalPlot.__init__(self, "Sum of average signals")

    def getGenerator(self):
        return Signal.SingleAverage(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()
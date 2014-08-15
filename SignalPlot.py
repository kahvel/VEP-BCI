__author__ = 'Anti'
import operator
import PlotWindow
import Signal


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
        print result
        return result


class MultipleRegular(SignalPlot, Signal.Multiple):
    def __init__(self):
        SignalPlot.__init__(self, "Signals")
        Signal.Multiple.__init__(self)

    def getGenerator(self):
        return Signal.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class SingleRegular(SignalPlot, Signal.Single):
    def __init__(self):
        SignalPlot.__init__(self, "Sum of signals")
        Signal.Single.__init__(self)

    def getGenerator(self):
        return Signal.SingleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class MultipleAverage(SignalPlot, Signal.Multiple):
    def __init__(self):
        SignalPlot.__init__(self, "Average signals")
        Signal.Multiple.__init__(self)

    def getGenerator(self):
        return Signal.MultipleAverage(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class SingleAverage(SignalPlot, Signal.Single):
    def __init__(self):
        SignalPlot.__init__(self, "Sum of average signals")
        Signal.Single.__init__(self)

    def getGenerator(self):
        return Signal.SingleAverage(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()
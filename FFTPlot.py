__author__ = 'Anti'
import PlotWindow
import FFT


class FFTPlot(PlotWindow.PlotWindow):
    def __init__(self, title):
        PlotWindow.PlotWindow.__init__(self, title)

    def startDeleting(self):
        return lambda x: True

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i*self.window_width/len(coordinates))
            result.append(self.scaleY(coordinates[i], index, self.plot_count, 3.3, 0.2))
        return result


class MultipleRegular(FFTPlot, FFT.Multiple):
    def __init__(self):
        FFTPlot.__init__(self, "FFTs")
        FFT.Multiple.__init__(self)

    def getGenerator(self):
        return FFT.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients)


class MultipleAverage(FFTPlot, FFT.Multiple):
    def __init__(self):
        FFTPlot.__init__(self, "Average FFTs")
        FFT.Multiple.__init__(self)

    def getGenerator(self):
        return FFT.MultipleAverage(self.options, self.window_function, self.channel_count, self.filter_coefficients)


class SingleAverage(FFTPlot, FFT.Single):
    def __init__(self):
        FFTPlot.__init__(self, "Sum of average FFTs")
        FFT.Single.__init__(self)

    def getGenerator(self):
        return FFT.SingleAverage(self.options, self.window_function, self.channel_count, self.filter_coefficients)


class SingleRegular(FFTPlot, FFT.Single):
    def __init__(self):
        FFTPlot.__init__(self, "Sum of FFTs")
        FFT.Single.__init__(self)

    def getGenerator(self):
        return FFT.SingleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients)
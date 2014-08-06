__author__ = 'Anti'
import PlotWindow
import FFT


class FFTPlot(PlotWindow.PlotWindow):
    def __init__(self, title):
        PlotWindow.PlotWindow.__init__(self, title)
        self.start_deleting = lambda x: True

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i*self.window_width/len(coordinates))
            result.append(self.scaleY(coordinates[i], index, self.plot_count, 3.3, 0.2))
        return result


class Multiple(PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self)

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(float(packet.sensors[self.sensor_names[i]]["value"]))


class Single(PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self)

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[0].send(float(packet.sensors[self.sensor_names[i]]["value"]))


class Regular(object):
    pass


class Average(object):
    pass


class MultipleRegular(FFTPlot, Multiple, Regular, FFT.MultipleRegular):
    def __init__(self):
        FFTPlot.__init__(self, "FFTs")
        Regular.__init__(self)
        Multiple.__init__(self)
        FFT.MultipleRegular.__init__(self)


class MultipleAverage(FFTPlot, Average, Multiple, FFT.MultipleAverage):
    def __init__(self):
        FFTPlot.__init__(self, "Average FFTs")
        Average.__init__(self)
        Multiple.__init__(self)
        FFT.MultipleAverage.__init__(self)


class SingleAverage(FFTPlot, Average, Single, FFT.SingleAverage):
    def __init__(self):
        FFTPlot.__init__(self, "Sum of average FFTs")
        Average.__init__(self)
        Single.__init__(self)
        FFT.SingleAverage.__init__(self)


class SingleRegular(FFTPlot, Regular, Single, FFT.SingleRegular):
    def __init__(self):
        FFTPlot.__init__(self, "Sum of FFTs")
        Regular.__init__(self)
        Single.__init__(self)
        FFT.SingleRegular.__init__(self)
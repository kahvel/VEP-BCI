__author__ = 'Anti'
import operator
import PlotWindow
import Signal
# import sklearn.cross_decomposition


class SignalPlot(PlotWindow.PlotWindow):
    def __init__(self, title):
        PlotWindow.PlotWindow.__init__(self, title)
        self.start_deleting = lambda packet_count: operator.eq(packet_count, self.options["Length"])

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(packet_count-len(coordinates), packet_count):
            result.append(i*self.window_width/self.options["Length"])
            result.append(self.scaleY(coordinates.popleft(),  index, self.plot_count, 10, -10))
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
        summ = 0
        for i in range(self.channel_count):
            summ += packet.sensors[self.sensor_names[i]]["value"]
        self.generators[0].send(float(summ)/self.channel_count)


class Average(object):
    pass


class Regular(object):
    pass


class MultipleRegular(SignalPlot, Regular, Multiple, Signal.Regular):
    def __init__(self):
        SignalPlot.__init__(self, "Signals")
        Regular.__init__(self)
        Multiple.__init__(self)
        Signal.Regular.__init__(self)


class SingleRegular(SignalPlot, Regular, Single, Signal.Regular):
    def __init__(self):
        SignalPlot.__init__(self, "Sum of signals")
        Regular.__init__(self)
        Single.__init__(self)
        Signal.Regular.__init__(self)


class MultipleAverage(SignalPlot, Average, Multiple, Signal.Average):
    def __init__(self):
        SignalPlot.__init__(self, "Average signals")
        Average.__init__(self)
        Multiple.__init__(self)
        Signal.Average.__init__(self)


class SingleAverage(SignalPlot, Average, Single, Signal.Average):
    def __init__(self):
        SignalPlot.__init__(self, "Sum of average signals")
        Average.__init__(self)
        Single.__init__(self)
        Signal.Average.__init__(self)


# class CCARegular(Signal, PlotWindow.SinglePlotWindow):
#     def __init__(self):
#         PlotWindow.SinglePlotWindow.__init__(self, "CCA signal plot")
#         Signal.__init__(self)
#
#     def getChannelAverage(self, index):
#         return sum(self.averages)/len(self.averages)
#
#     def coordinates_generator(self):
#         # average = [0 for _ in range(513)]
#         coordinates = []
#         cca = sklearn.cross_decomposition.CCA()
#         for _ in range(self.channel_count):
#             coordinates.append([0 for _ in range(512)])
#         yield
#         while True:
#             for i in range(512):
#                 for j in range(self.channel_count):
#                     y = yield
#                     coordinates[j][i] = y
#             # for i in range(self.channel_count):
#             print coordinates
#             # asd = [[i for i in range(1, 513)] for _ in range(2)]
#             # print asd
#             x = np.array(coordinates[0])
#             x.shape = 512,1
#             y = np.array(coordinates[1])
#             y.shape = 512,1
#             print x
#             print x.shape
#             print y
#             print y.shape
#             xa, ya = cca.fit_transform(x, y)
#             print xa
#             print ya
#             # for i in range(len(ffts[0])):
#             #     sum = 0
#             #     for j in range(self.channel_count):
#             #         sum += ffts[j][i]
#             #     average[i] = sum/self.channel_count
#             yield Queue.deque(x)
#
#     def sendPacket(self, packet):
#         for i in range(self.channel_count):
#             self.generators[0].send(packet.sensors[self.all_sensor_names[i]]["value"])
#
#     def getGenerator(self, i):
#         return self.plot_generator(i, self.channel_count*512, lambda packet_count: operator.eq(packet_count, 512))
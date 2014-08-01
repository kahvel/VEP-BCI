__author__ = 'Anti'
import Queue
import operator
import PlotWindow
# import sklearn.cross_decomposition
import numpy as np
import scipy.signal
import copy


class Signal(object):
    def __init__(self):
        self.start_deleting = lambda packet_count: operator.eq(packet_count, self.length)

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(packet_count-len(coordinates), packet_count):
            result.append(i*self.window_width/self.length)
            result.append(self.scaleY(coordinates.popleft(),  index, self.plot_count))
        return result

    def addPrevious(self, signal, previous):
        if isinstance(signal, list):
            return [previous] + signal
        else:
            return np.insert(signal, 0, previous)

    def filterSignal(self, signal):
        if self.filter:
            result, self.filter_prev_state = scipy.signal.lfilter(self.filter_coefficients, 1.0, signal, zi=self.filter_prev_state)
            return result
        else:
            return signal

    def setInitSignal(self, min_packet, max_packet, averages, init_coordinates):
        self.min_packet = min_packet
        self.max_packet = max_packet
        self.averages = averages
        self.init_coordinates = copy.deepcopy(init_coordinates)

    def signalPipeline(self, signal, i, prev_coordinate):
        filtered_signal = self.filterSignal(signal)
        window_segment = self.getSegment(self.window_function, i)
        windowed_signal = self.windowSignal(filtered_signal, window_segment)
        extended_signal = self.addPrevious(windowed_signal, prev_coordinate)
        return extended_signal


class Multiple(object):
    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(float(packet.sensors[self.sensor_names[i]]["value"]-self.averages[i]))


class Single(object):
    def sendPacket(self, packet):
        summ = 0
        for i in range(self.channel_count):
            summ += packet.sensors[self.sensor_names[i]]["value"]
        self.generators[0].send(float(summ)/self.channel_count-float(sum(self.averages))/len(self.averages))


class Average(object):
    def coordinates_generator(self, index):
        average = [0 for _ in range(self.length)]
        k = 0
        prev_coordinate = 0
        yield
        self.filter_prev_state = self.filterPrevState(self.init_coordinates[index])
        while True:
            k += 1
            for i in range(self.length/self.step):
                for j in range(self.step):
                    y = yield
                    average[i*self.step+j] = (average[i*self.step+j] * (k - 1) + y) / k
                signal_segment = self.getSegment(average, i)
                result = self.signalPipeline(signal_segment, i, prev_coordinate)
                yield Queue.deque(result)
                prev_coordinate = result[-1]


class Regular(object):
    def coordinates_generator(self, index):
        average = [0 for _ in range(self.step)]
        prev_coordinate = 0
        yield
        self.filter_prev_state = self.filterPrevState(self.init_coordinates[index])
        while True:
            for i in range(self.length/self.step):
                for j in range(self.step):
                    y = yield
                    average[j] = y
                result = self.signalPipeline(average, i, prev_coordinate)
                yield Queue.deque(result)
                prev_coordinate = result[-1]


class MultipleRegular(Signal, Regular, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Signals")
        Signal.__init__(self)
        Regular.__init__(self)
        Multiple.__init__(self)


class SingleRegular(Signal, Regular, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Sum of signals")
        Signal.__init__(self)
        Regular.__init__(self)
        Single.__init__(self)


class MultipleAverage(Signal, Average, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Average signals")
        Signal.__init__(self)
        Average.__init__(self)
        Multiple.__init__(self)


class SingleAverage(Signal, Average, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Sum of average signals")
        Signal.__init__(self)
        Average.__init__(self)
        Single.__init__(self)


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
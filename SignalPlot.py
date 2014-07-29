__author__ = 'Anti'
import Queue
import operator
import PlotWindow
# import sklearn.cross_decomposition
import numpy as np


class Signal(object):
    def __init__(self):
        self.start_deleting = lambda packet_count: operator.eq(packet_count, self.length)

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(packet_count-len(coordinates), packet_count):
            result.append(i*self.window_length/self.length)
            result.append(self.scaleY(coordinates.popleft(),  index, self.plot_count))
        return result

    def scaleY(self, y,  index, plot_count):
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        return ((((y - self.min_packet[index]) * (-100 - 100)) / (self.max_packet[index] - self.min_packet[index])) + 100
                + index*self.window_height + self.window_height/2) / plot_count

    def addPrevious(self, signal, previous):
        if isinstance(signal, list):
            return [previous] + signal
        else:
            return np.insert(signal, 0, previous)

    def getSegment(self, array, i):
        if self.window:
            return array[i*self.step:i*self.step+self.step]
        else:
            return None

    def setInitSignal(self, min_packet, max_packet, averages, initial_packets):
        self.min_packet = min_packet
        self.max_packet = max_packet
        self.averages = averages
        self.initial_packets = initial_packets[:]


class Multiple(object):
    def getChannelAverage(self, index):
        return self.averages[index]

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"]-self.averages[i])


class Single(object):
    def getChannelAverage(self, index):
        return sum(self.averages)/len(self.averages)

    def sendPacket(self, packet):
        summ = 0
        for i in range(self.channel_count):
            summ += packet.sensors[self.sensor_names[i]]["value"]
        self.generators[0].send(summ/self.channel_count-sum(self.averages)/len(self.averages))


class Average(object):
    def coordinates_generator(self, index):
        average = [0 for _ in range(self.length)]
        k = 0
        prev = 0
        yield
        self.prev_filter = self.filterInitState(index)
        while True:
            k += 1
            for i in range(self.length/self.step):
                for j in range(self.step):
                    y = yield
                    average[i*self.step+j] = (average[i*self.step+j] * (k - 1) + y) / k
                signal_segment = average[i*self.step:i*self.step+self.step]
                filtered_signal = self.filterSignal(signal_segment)
                window_segment = self.getSegment(self.window_function, i)
                windowed_signal = self.windowSignal(filtered_signal, window_segment)
                extended_signal = self.addPrevious(windowed_signal, prev)
                yield Queue.deque(extended_signal)
                prev = extended_signal[-1]


class Regular(object):
    def coordinates_generator(self, index):
        average = [0 for _ in range(self.step)]
        prev = 0
        yield
        self.prev_filter = self.filterInitState(index)
        while True:
            for i in range(self.length/self.step):
                for j in range(self.step):
                    y = yield
                    average[j] = y
                filtered_signal = self.filterSignal(average)
                window_segment = self.getSegment(self.window_function, i)
                windowed_signal = self.windowSignal(filtered_signal, window_segment)
                extended_signal = self.addPrevious(windowed_signal, prev)
                yield Queue.deque(extended_signal)
                prev = extended_signal[-1]


class MultipleRegular(Signal, Regular, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Multiple regular signal plot")
        Signal.__init__(self)
        Regular.__init__(self)
        Multiple.__init__(self)


class SingleRegular(Signal, Regular, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Single regular signal plot")
        Signal.__init__(self)
        Regular.__init__(self)
        Single.__init__(self)


class MultipleAverage(Signal, Average, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Multiple average signal plot")
        Signal.__init__(self)
        Average.__init__(self)
        Multiple.__init__(self)


class SingleAverage(Signal, Average, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Single average signal plot")
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
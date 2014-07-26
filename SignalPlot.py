__author__ = 'Anti'
import Queue
import operator
import PlotWindow
import sklearn.cross_decomposition
import numpy as np


class Signal(object):
    def __init__(self):
        self.averages = []
        self.min = []
        self.max = []

    def calculateAverage(self, packets):
        self.min = []
        self.max = []
        self.averages = []
        asd = []
        for i in range(self.channel_count):
            asd.append([])
            for j in range(len(packets)):
                asd[i].append(packets[j].sensors[self.sensor_names[i]]["value"])
        for i in range(self.channel_count):
            self.averages.append(sum(asd[i])/len(asd[i]))
            self.min.append(min(asd[i])-self.averages[i])
            self.max.append(max(asd[i])-self.averages[i])
        print self.averages, self.min, self.max
        # self.averages = [0 for _ in range(self.channel_count)]
        # for j in range(1, len(packets)+1):
        #     for i in range(self.channel_count):
        #         self.averages[i] = (self.averages[i] * (j - 1) + packets[j-1].sensors[self.sensor_names[i]]["value"]*self.window_function[j-1]) / j
        # print(self.averages)

    def getGenerator(self, i):
        return self.plot_generator(i, lambda packet_count: operator.eq(packet_count, self.length))

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(packet_count-len(coordinates), packet_count):
            result.append(i*self.window_length/self.length)
            result.append(self.scaleY(coordinates.popleft(),  index, self.plot_count))
        return result

    def scaleY(self, y,  index, plot_count):
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        return ((((y - self.min[index]) * (-100 - 100)) / (self.max[index] - self.min[index])) + 100
                + index*self.window_height + self.window_height/2) / plot_count
        # return ((y-average) + index*self.window_height + self.window_height/2) / plot_count


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
    def coordinates_generator(self):
        average = [0 for _ in range(self.length)]
        k = 0
        prev = [0]
        prev_window = [0]
        yield
        while True:
            k += 1
            for i in range(self.length/self.step):
                for j in range(self.step):
                    y = yield
                    average[i*self.step+j] = (average[i*self.step+j] * (k - 1) + y) / k
                yield Queue.deque(np.insert(self.window_function[i*self.step:i*self.step+self.step], 0, prev_window)*(prev+average[i*self.step:i*self.step+self.step]))
                prev_window = self.window_function[i*self.step:i*self.step+self.step][-1]
                prev = [average[i*self.step+self.step-1]]


class Regular(object):
    def coordinates_generator(self):
        average = [0 for _ in range(self.step)]
        prev = [0]
        prev_window = [0]
        yield
        while True:
            for j in range(self.length/self.step):
                for i in range(self.step):
                    y = yield
                    average[i] = y
                yield Queue.deque(np.insert(self.window_function[j*self.step:j*self.step+self.step], 0, prev_window)*(prev+average))
                prev_window = self.window_function[j*self.step:j*self.step+self.step][-1]
                prev = [average[-1]]


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
#             self.generators[0].send(packet.sensors[self.sensor_names[i]]["value"])
#
#     def getGenerator(self, i):
#         return self.plot_generator(i, self.channel_count*512, lambda packet_count: operator.eq(packet_count, 512))
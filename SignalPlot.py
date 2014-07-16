__author__ = 'Anti'
import Queue
import operator
import PlotWindow


class Signal(object):
    def __init__(self):
        self.averages = []

    def calculateAverage(self, packets):
        self.averages = [0 for _ in range(self.channel_count)]
        for j in range(1, len(packets)+1):
            for i in range(self.channel_count):
                self.averages[i] = (self.averages[i] * (j - 1) + packets[j-1].sensors[self.sensor_names[i]]["value"]) / j
        print(self.averages)

    def getGenerator(self, i):
        return self.generator(i, 8, lambda packet_count: operator.eq(packet_count, 512))

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(packet_count-len(coordinates), packet_count):
            result.append(i)
            result.append(self.scaleY(coordinates.popleft(), self.getChannelAverage(index), index, self.plot_count))
        return result

    def scaleY(self, y, average, index, plot_count):
        return ((y-average) + index*512 + 512/2) / plot_count


class Multiple(object):
    def getChannelAverage(self, index):
        return self.averages[index]

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])


class Single(object):
    def getChannelAverage(self, index):
        return sum(self.averages)/len(self.averages)

    def sendPacket(self, packet):
        sum = 0
        for i in range(self.channel_count):
            sum += packet.sensors[self.sensor_names[i]]["value"]
        self.generators[0].send(sum/self.channel_count)


class Average(object):
    def gen(self):
        average = [0 for _ in range(512)]
        k = 0
        prev = [0]
        yield
        while True:
            k += 1
            for i in range(64):
                for j in range(8):
                    y = yield
                    average[i*8+j] = (average[i*8+j] * (k - 1) + y) / k
                yield Queue.deque(prev+average[i*8:i*8+8])
                prev = [average[i*8+8-1]]


class Regular(object):
    def gen(self):
        average = [0 for _ in range(8)]
        prev = [0]
        yield
        while True:
            for i in range(8):
                y = yield
                average[i] = y
            yield Queue.deque(prev+average)
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
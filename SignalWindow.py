__author__ = 'Anti'
import Tkinter
import MyWindows
import Queue


def scaleY(y, average, index, plot_count):
    return ((y-average) + index*512 + 512/2) / plot_count


def resetAverage(average):
    for i in range(len(average)):
        if i % 2 == 0:
            average[i] = i/2
        else:
            average[i] = 0


class AbstractSignalWindow(MyWindows.ToplevelWindow):
    def __init__(self, title):
        MyWindows.ToplevelWindow.__init__(self, title, 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.continue_generating = True
        self.canvas.pack()
        self.plot_count = 0
        self.channel_count = 0
        self.sensor_names = []
        self.generators = []
        self.averages = []

    # def addGenCleanup(self):
    #     self.protocol("WM_DELETE_WINDOW", self.exit2)
    #
    # def removeGenCleanup(self):
    #     self.protocol("WM_DELETE_WINDOW", self.exit)
    #
    # def exit2(self):
    #     self.continue_generating = False

    def calculateAverage(self, packets):
        self.averages = [0 for _ in range(self.channel_count)]
        for j in range(1, len(packets)+1):
            for i in range(self.channel_count):
                self.averages[i] = (self.averages[i] * (j - 1) + packets[j-1].sensors[self.sensor_names[i]]["value"]) / j
        print(self.averages)

    def setup(self, checkbox_values, sensor_names):
        self.channel_count = 0
        self.sensor_names = []
        self.generators = []
        # self.addGenCleanup()
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.sensor_names.append(sensor_names[i])
                self.channel_count += 1
        self.setPlotCount()
        for i in range(self.plot_count):
            self.generators.append(self.generator(i))
            self.generators[i].send(None)

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(packet_count-len(coordinates), packet_count):
            result.append(i)
            result.append(scaleY(coordinates.popleft(), self.getChannelAverage(index), index, self.plot_count))
        return result

    def generator(self, index):
        average_generator = self.gen()
        try:
            lines = []
            packet_count = 0
            delete = False
            average_generator.send(None)
            while True:
                y = yield
                avg = average_generator.send(y)
                if packet_count % 8 == 0 and packet_count != 0:
                    scaled_avg = self.scale(avg, index, packet_count)
                    lines.append(self.canvas.create_line(scaled_avg))
                    average_generator.next()
                    if packet_count == 512:
                        packet_count = 0
                        delete = True
                    if delete:
                        self.canvas.delete(lines[0])
                        del lines[0]
                    if index == self.plot_count-1:
                        self.canvas.update()
                packet_count += 1
        finally:
            print "closing average generator"
            average_generator.close()


class SignalWindow(AbstractSignalWindow):
    def __init__(self):
        AbstractSignalWindow.__init__(self, "Plot")
        self.canvas.configure(xscrollincrement="1")

    def setPlotCount(self):
        self.plot_count = self.channel_count

    def getChannelAverage(self, index):
        return self.averages[index]

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])

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

    # def generator(self, index):
    #     prev = 0, 0
    #     lines = [self.canvas.create_line(prev, prev)]
    #     packet_count = 0
    #     coordinates = []
    #     while True:
    #         y = yield self.continue_generating
    #         if not self.continue_generating:
    #             return
    #         coordinates.append(packet_count)
    #         coordinates.append(scaleY(y, self.averages[index], index, self.plot_count))
    #         if packet_count % 10 == 0:
    #             lines.append(self.canvas.create_line(prev, coordinates))
    #             prev = packet_count, coordinates[-1]
    #             coordinates = []
    #             if packet_count > 512:
    #                 self.canvas.delete(lines[0])
    #                 del lines[0]
    #         if index == self.plot_count-1:
    #             if packet_count % 2 == 0:
    #                 if packet_count > 512:
    #                     self.canvas.xview_scroll(2, Tkinter.UNITS)
    #                 self.canvas.update()
    #         packet_count += 1


class AbstractAverageSignal(AbstractSignalWindow):
    def __init__(self, title):
        AbstractSignalWindow.__init__(self, title)

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


class AverageSignalWindow(AbstractAverageSignal):
    def __init__(self):
        AbstractAverageSignal.__init__(self, "Average Plot")

    def getChannelAverage(self, index):
        return self.averages[index]

    def setPlotCount(self):
        self.plot_count = self.channel_count

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])


class AverageSignalWindow2(AbstractAverageSignal):
    def __init__(self):
        AbstractAverageSignal.__init__(self, "Average Plot")
        #self.average = sum(self.averages)/len(self.averages)

    def getChannelAverage(self, index):
        return sum(self.averages)/len(self.averages)

    def setPlotCount(self):
        self.plot_count = 1

    def sendPacket(self, packet):
        sum = 0
        for i in range(self.channel_count):
            sum += packet.sensors[self.sensor_names[i]]["value"]
        self.generators[0].send(sum/self.channel_count)
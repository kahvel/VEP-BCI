__author__ = 'Anti'
import Tkinter
import MyWindows


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
        self.averages = [0 for _ in range(self.plot_count)]
        for j in range(1, len(packets)+1):
            for i in range(self.plot_count):
                self.averages[i] = (self.averages[i] * (j - 1) + packets[j-1].sensors[self.sensor_names[i]]["value"]) / j
        print(self.averages)


class SignalWindow(AbstractSignalWindow):
    def __init__(self):
        AbstractSignalWindow.__init__(self, "Plot")
        self.canvas.configure(xscrollincrement="1")

    def setup(self, checkbox_values, sensor_names):
        self.plot_count = 0
        self.sensor_names = []
        # self.addGenCleanup()
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.sensor_names.append(sensor_names[i])
                self.generators.append(self.generator(self.plot_count))
                self.generators[self.plot_count].send(None)
                self.plot_count += 1

    def sendPacket(self, packet):
        for i in range(self.plot_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])

    def generator(self, index):
        lines = []
        x = 512
        prev = 512, 0
        lines.append(self.canvas.create_line(prev, prev))
        while True:
            coordinates = []
            for i in range(0, 10, 2):  # get 10 values before drawing new line
                for _ in range(2):     # get 2 values before scrolling
                    x += 1
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        return
                    coordinates.append(x)
                    coordinates.append(scaleY(y, self.averages[index], index, self.plot_count))
                if index == self.plot_count-1:
                    self.canvas.xview_scroll(2, Tkinter.UNITS)
                    self.canvas.update()
            lines.append(self.canvas.create_line(prev, coordinates))
            prev = x, coordinates[-1]
            if x > 1024:  # x value starts at 512
                self.canvas.delete(lines[0])
                del lines[0]


class AverageSignalWindow(AbstractSignalWindow):
    def __init__(self):
        AbstractSignalWindow.__init__(self, "Average Plot")

    def resetAverage(self, average):
        resetAverage(average)

    def setup(self, checkbox_values, sensor_names):
        self.plot_count = 0
        self.sensor_names = []
        # self.addGenCleanup()
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.sensor_names.append(sensor_names[i])
                self.generators.append(self.generator(self.plot_count))
                self.generators[self.plot_count].send(None)
                self.plot_count += 1

    def sendPacket(self, packet):
        for i in range(self.plot_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])

    def generator(self, index):
        coordinates = [0 for _ in range(1024)]
        self.resetAverage(coordinates)
        line = self.canvas.create_line(0, 0, 0, 0)
        j = 0
        while True:
            j += 1
            for i in range(1, 1024, 2):  # get 512 values before drawing new line
                y = yield self.continue_generating
                if not self.continue_generating:
                    return
                if y == "Reset":
                    j = 0
                    self.resetAverage(coordinates)
                    break
                coordinates[i] = (coordinates[i] * (j - 1) + scaleY(y, self.averages[index], index, self.plot_count)) / j
            self.canvas.delete(line)
            line = self.canvas.create_line(coordinates)
            if index == self.plot_count-1:
                self.canvas.update()


class AverageSignalWindow2(AbstractSignalWindow):
    def __init__(self):
        AbstractSignalWindow.__init__(self, "Average Plot")

    def resetAverage(self, average):
        resetAverage(average)

    def setup(self, checkbox_values, sensor_names):
        self.plot_count = 0
        self.sensor_names = []
        # self.addGenCleanup()
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.sensor_names.append(sensor_names[i])
                self.plot_count += 1
        self.generators.append(self.generator())
        self.generators[0].send(None)

    def sendPacket(self, packet):
        for i in range(self.plot_count):
            self.generators[0].send(packet.sensors[self.sensor_names[i]]["value"])

    def generator(self, index=0):
        coordinates = [0 for _ in range(1024)]
        self.resetAverage(coordinates)
        line = self.canvas.create_line(0, 0, 0, 0)
        j = 0
        while True:
            j += 1
            for i in range(1, 1024, 2):      # get 512 values before drawing
                for l in range(self.plot_count):  # get value for each channel
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        return
                    if y == "Reset":
                        j = 0
                        self.resetAverage(coordinates)
                        break
                    coordinates[i] = (coordinates[i] * (j - 1) + scaleY(y, self.averages[l], index, 1)) / j
                else:
                    continue
                break
            self.canvas.delete(line)
            line = self.canvas.create_line(coordinates)
            self.canvas.update()
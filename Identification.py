__author__ = 'Anti'
import MyWindows
import numpy as np
import scipy.signal
import Tkinter
import ScrolledText


class Abstract(MyWindows.ToplevelWindow):
    def __init__(self, title):
        MyWindows.ToplevelWindow.__init__(self, title, 200, 200)
        self.channel_count = 0
        self.sensor_names = []
        self.generators = []
        self.continue_generating = True
        self.freq_points = []
        self.freq_indexes = []
        self.packet_count = 128
        # self.canvas = Tkinter.Canvas(self, width=200, height=200)
        # self.canvas.pack()
        self.canvas = ScrolledText.ScrolledText(self, width=200, height=200)
        self.canvas.pack()

    def setup(self, checkbox_values, sensor_names, freq_points):
        self.freq_indexes = []
        self.freq_points = freq_points

        self.channel_count = 0
        self.sensor_names = []
        self.generators = []
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.sensor_names.append(sensor_names[i])
                self.channel_count += 1
        if self.channel_count == 0:
            self.continue_generating = False
            print "No channels chosen"
            return
        self.setPlotCount()
        for i in range(self.plot_count):
            self.generators.append(self.getGenerator(i))
            self.generators[i].send(None)

    def generator(self, index, update_after, start_deleting):
        coordinates_generator = self.coordinate_generator(128)
        try:
            packet_count = 0
            for freq in self.freq_points:
                self.freq_indexes.append(freq*self.packet_count/128)
            coordinates_generator.send(None)
            while True:
                y = yield
                coordinates = coordinates_generator.send(y)
                if packet_count % update_after == 0 and packet_count != 0:
                    if start_deleting(packet_count):
                        packet_count = 0
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]]*2/(coordinates[self.freq_indexes[i]-1]+coordinates[self.freq_indexes[i]+1])
                        if ratio > max:
                            max = ratio
                            max_index = i
                        # print ratio,
                    if max < 1:
                        print "Ratio < 1",
                    # print self.freq_points[max_index]
                    # self.canvas.create_text(10, 10+10*index, text=self.freq_points[max_index])
                    self.canvas.insert(Tkinter.INSERT, str(self.freq_points[max_index])+" ")
                    coordinates_generator.next()
                packet_count += 1
        finally:
            print "Closing generator"
            coordinates_generator.close()


class PS2(Abstract):
    def __init__(self):
        Abstract.__init__(self, "PS2")

    def setPlotCount(self):
        self.plot_count = self.channel_count

    def getGenerator(self, i):
        return self.generator(i, 128, lambda x: True)

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])

    def coordinate_generator(self, packet_count):
        average = [0 for _ in range(packet_count)]
        yield
        while True:
            for i in range(packet_count):
                y = yield
                average[i] = y
            yield np.log10(np.abs(np.fft.rfft(scipy.signal.detrend(average))))


class PS(Abstract):
    def __init__(self):
        Abstract.__init__(self, "PS")

    def setPlotCount(self):
        self.plot_count = 1

    def getGenerator(self, i):
        return self.generator(i, 128*self.channel_count, lambda x: True)

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[0].send(packet.sensors[self.sensor_names[i]]["value"])

    def coordinate_generator(self, packet_count):
        average = [0 for _ in range(packet_count/2+1)]
        coordinates = []
        for _ in range(self.channel_count):
            coordinates.append([0 for _ in range(packet_count)])
        yield
        while True:
            for i in range(packet_count):
                for j in range(self.channel_count):
                    y = yield
                    coordinates[j][i] = y
            ffts = []
            for i in range(self.channel_count):
                ffts.append(np.abs(np.fft.rfft(scipy.signal.detrend(coordinates[i]))))
            for i in range(len(ffts[0])):
                sum = 0
                for j in range(self.channel_count):
                    sum += ffts[j][i]
                average[i] = sum/self.channel_count
            yield np.log10(average)
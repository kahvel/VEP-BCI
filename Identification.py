__author__ = 'Anti'
import MyWindows
import numpy as np
import scipy.signal
import Tkinter
import ScrolledText


class Abstract(MyWindows.ToplevelWindow):
    def __init__(self, title):
        MyWindows.ToplevelWindow.__init__(self, title, 525, 200)
        self.channel_count = 0
        self.sensor_names = []
        self.generators = []
        self.continue_generating = True
        self.freq_points = []
        self.freq_indexes = []
        self.length = 512
        self.step = 32
        self.window_function = 1
        self.headset_freq = 128
        self.canvas = ScrolledText.ScrolledText(self, width=200, height=200)
        self.canvas.pack()

    def setOptions(self, window_var, options_textboxes):
        self.length = int(options_textboxes["Length"].get())
        self.step = int(options_textboxes["Step"].get())
        window_var = window_var.get()
        if window_var == "hanning":
            self.window_function = np.hanning(self.length)
        elif window_var == "hamming":
            self.window_function = np.hamming(self.length)
        elif window_var == "blackman":
            self.window_function = np.blackman(self.length)
        elif window_var == "kaiser":
            self.window_function = np.kaiser(self.length, float(options_textboxes["Beta"].get()))
        elif window_var == "bartlett":
            self.window_function = np.bartlett(self.length)
        elif window_var == "None":
            self.window_function = 1

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
        coordinates_generator = self.coordinates_generator()
        try:
            packet_count = 0
            for freq in self.freq_points:
                self.freq_indexes.append(freq*self.length/self.headset_freq)
                print np.fft.rfftfreq(self.length)[self.freq_indexes[-1]]*self.headset_freq
            coordinates_generator.send(None)
            while True:
                y = yield
                coordinates = coordinates_generator.send(y)
                if coordinates is not None:
                    if start_deleting(packet_count):
                        packet_count = 0
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]-1]#*2/(coordinates[self.freq_indexes[i]-2]+coordinates[self.freq_indexes[i]])
                        ratio2 = coordinates[self.freq_indexes[i]/2-1]#*2/(coordinates[self.freq_indexes[i]/2-2]+coordinates[self.freq_indexes[i]/2])
                        ratio3 = coordinates[self.freq_indexes[i]/4-1]
                        if ratio> max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]/2-1]#*2/(coordinates[self.freq_indexes[i]/2-2]+coordinates[self.freq_indexes[i]/2])
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]/4-1]#*2/(coordinates[self.freq_indexes[i]/4-2]+coordinates[self.freq_indexes[i]/4])
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"\n")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]-1]*2/(coordinates[self.freq_indexes[i]-2]+coordinates[self.freq_indexes[i]])
                        # ratio2 = coordinates[self.freq_indexes[i]/2-1]*2/(coordinates[self.freq_indexes[i]/2-2]+coordinates[self.freq_indexes[i]/2])
                        if ratio> max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]/2-1]*2/(coordinates[self.freq_indexes[i]/2-2]+coordinates[self.freq_indexes[i]/2])
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]/4-1]*2/(coordinates[self.freq_indexes[i]/4-2]+coordinates[self.freq_indexes[i]/4])
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"\n\n")
                    self.canvas.yview(Tkinter.END)
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
        return self.generator(i, self.length, lambda x: True)

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])

    def coordinates_generator(self):
        coordinates = [0 for _ in range(self.length)]
        yield
        for i in range(self.length):
            y = yield
            coordinates[i] = y
        yield np.log10(np.abs(np.fft.rfft(self.window_function*scipy.signal.detrend(coordinates))))
        while True:
            for i in range(self.length/self.step):
                for j in range(self.step):
                    y = yield
                    coordinates[i*self.step+j] = y
                yield np.log10(np.abs(np.fft.rfft(self.window_function*scipy.signal.detrend(coordinates))))


class PS(Abstract):
    def __init__(self):
        Abstract.__init__(self, "PS")

    def setPlotCount(self):
        self.plot_count = 1

    def getGenerator(self, i):
        return self.generator(i, self.length*self.channel_count, lambda x: True)

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[0].send(packet.sensors[self.sensor_names[i]]["value"])

    def coordinates_generator(self):
        average = [0 for _ in range(self.length//2+1)]
        coordinates = []
        for _ in range(self.channel_count):
            coordinates.append([0 for _ in range(self.length)])
        k = 0
        yield
        for i in range(self.length):
            for j in range(self.channel_count):
                y = yield
                coordinates[j][i] = y
        k += 1
        ffts = []
        for i in range(self.channel_count):
            ffts.append(np.abs(np.fft.rfft(self.window_function*scipy.signal.detrend(coordinates[i]))))
        for i in range(len(ffts[0])):
            sum = 0
            for j in range(self.channel_count):
                sum += ffts[j][i]
            average[i] = (average[i] * (k - 1) + sum/self.channel_count) / k
        yield np.log10(average)
        while True:
            for i in range(self.length/self.step):
                for j in range(self.step):
                    for channel in range(self.channel_count):
                        y = yield
                        coordinates[channel][i*self.step+j] = y
                k += 1
                ffts = []
                for i in range(self.channel_count):
                    ffts.append(np.abs(np.fft.rfft(self.window_function*scipy.signal.detrend(coordinates[i]))))
                for i in range(len(ffts[0])):
                    sum = 0
                    for j in range(self.channel_count):
                        sum += ffts[j][i]
                    average[i] = (average[i] * (k - 1) + sum/self.channel_count) / k
                yield np.log10(average)
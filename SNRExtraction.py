__author__ = 'Anti'
import numpy as np
import scipy.signal
import Tkinter
import ScrolledText
import ControllableWindow
import FFT


class Abstract(ControllableWindow.ControllableWindow, FFT.FFT):
    def __init__(self, title):
        ControllableWindow.ControllableWindow.__init__(self, title, 525, 200)
        FFT.FFT.__init__(self)
        self.canvas = ScrolledText.ScrolledText(self)
        self.canvas.pack()
        self.freq_points = []
        self.freq_indexes = []

    def setInitSignal(self, min_packet, max_packet, averages, init_coordinates):
        self.init_coordinates = init_coordinates
        self.averages = averages

    def generator(self, index, start_deleting):
        coordinates_generator = self.coordinates_generator(index)
        detected_freq = None
        try:
            packet_count = 0
            for freq in self.freq_points:
                self.freq_indexes.append(int(freq*self.length/self.headset_freq))
                print np.fft.rfftfreq(self.length)[self.freq_indexes[-1]]*self.headset_freq
            coordinates_generator.send(None)
            while True:
                y = yield detected_freq
                detected_freq = None
                coordinates = coordinates_generator.send(y)
                if coordinates is not None:
                    if start_deleting(packet_count):
                        packet_count = 0
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]-1]
                        if ratio> max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]/2-1]
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]/4-1]
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"\n")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]-1]*2/(coordinates[self.freq_indexes[i]-2]+coordinates[self.freq_indexes[i]])
                        if ratio> max:
                            max = ratio
                            max_index = i
                    detected_freq = self.freq_points[max_index]
                    # print coordinates[self.freq_indexes[i]-3], coordinates[self.freq_indexes[i]-2], \
                    #     coordinates[self.freq_indexes[i]-1], coordinates[self.freq_indexes[i]],\
                    #     coordinates[self.freq_indexes[i]+1], coordinates[self.freq_indexes[i]+2]
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


class SNR(Abstract):
    def __init__(self):
        Abstract.__init__(self, "SNR")

    def setPlotCount(self):
        self.plot_count = self.channel_count

    def sendPacket(self, packet):
        ret = self.generators[0].send(float(packet.sensors[self.sensor_names[0]]["value"]-self.averages[0]))
        for i in range(1, self.channel_count):
            self.generators[i].send(float(packet.sensors[self.sensor_names[i]]["value"]-self.averages[i]))
        return ret

    def coordinates_generator(self, index):
        yield
        coordinates = self.init_coordinates[index]
        self.filter_prev_state = self.filterPrevState([0])
        while True:
            for i in range(self.length/self.step):
                del coordinates[:self.step]
                for j in range(self.step):
                    y = yield
                    coordinates.append(y)
                spectrum = self.signalPipeline(coordinates)
                yield self.normaliseSpectrum(spectrum)


class SumSNR(Abstract):
    def __init__(self):
        Abstract.__init__(self, "Sum SNR")

    def setPlotCount(self):
        self.plot_count = 1

    def sendPacket(self, packet):
        ret = self.generators[0].send(float(packet.sensors[self.sensor_names[0]]["value"]-self.averages[0]))
        for i in range(1, self.channel_count):
            self.generators[0].send(float(packet.sensors[self.sensor_names[i]]["value"]-self.averages[i]))
        return ret

    def coordinates_generator(self, index):
        average = [0 for _ in range(self.length//2+1)]
        yield
        coordinates = [self.init_coordinates[i] for i in range(self.channel_count)]
        self.filter_prev_state = self.filterPrevState([0])
        while True:
            for _ in range(self.length/self.step):
                for j in range(self.step):
                    for channel in range(self.channel_count):
                        y = yield
                        del coordinates[channel][0]
                        coordinates[channel].append(y)
                ffts = []
                for i in range(self.channel_count):
                    ffts.append(self.signalPipeline(coordinates[i]))
                for i in range(len(ffts[0])):
                    summ = 0
                    for j in range(self.channel_count):
                        summ += ffts[j][i]
                    average[i] = summ/self.channel_count
                yield self.normaliseSpectrum(average)
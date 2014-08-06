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
        self.freq_points = None
        self.freq_indexes = None
        self.recorded_signals = None

    def resetCanvas(self):
        self.canvas.insert(Tkinter.END, "Starting\n")

    def setup(self, options_textboxes, variables, sensor_names, freq_points=None):
        self.freq_points = freq_points
        self.freq_indexes = []
        self.recorded_signals = []
        ControllableWindow.ControllableWindow.setup(self, options_textboxes, variables, sensor_names)

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
                    detected_freq = self.freq_points[max_index]
                    # print np.argmax(coordinates[self.freq_indexes[i]-3:self.freq_indexes])
                    # print max_index, coordinates[self.freq_indexes[max_index]-3], coordinates[self.freq_indexes[max_index]-2], \
                    #     coordinates[self.freq_indexes[max_index]-1], coordinates[self.freq_indexes[max_index]],\
                    #     coordinates[self.freq_indexes[max_index]+1], coordinates[self.freq_indexes[max_index]+2]
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
        ret = None
        for i in range(self.channel_count):
            if ret is None:
                ret = self.generators[i].send(float(packet.sensors[self.sensor_names[i]]["value"]))
            else:
                self.generators[i].send(float(packet.sensors[self.sensor_names[i]]["value"]))
        return ret

    def coordinates_generator(self, index):
        coordinates = []
        filter_prev_state = self.filterPrevState([0])
        for i in range(self.length/self.step):
            segment = []
            for j in range(self.step):
                y = yield
                segment.append(y)
            result, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
            coordinates.extend(result)
        spectrum = self.signalPipeline(coordinates)
        yield self.normaliseSpectrum(spectrum)
        while True:
            for i in range(self.length/self.step):
                segment = []
                for j in range(self.step):
                    y = yield
                    segment.append(y)
                result, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
                coordinates.extend(result)
                del coordinates[:self.step]
                spectrum = self.signalPipeline(coordinates)
                yield self.normaliseSpectrum(spectrum)


class SumSNR(Abstract):
    def __init__(self):
        Abstract.__init__(self, "Sum SNR")

    def setPlotCount(self):
        self.plot_count = 1

    def sendPacket(self, packet):
        ret = None
        for i in range(self.channel_count):
            if ret is None:
                ret = self.generators[0].send(float(packet.sensors[self.sensor_names[i]]["value"]))
            else:
                self.generators[0].send(float(packet.sensors[self.sensor_names[i]]["value"]))
        return ret

    def coordinates_generator(self, index):
        average = []
        coordinates = [[] for _ in range(self.channel_count)]
        filter_prev_state = [self.filterPrevState([0]) for _ in range(self.channel_count)]
        for _ in range(self.length/self.step):
            segment = [[] for _ in range(self.channel_count)]
            for j in range(self.step):
                for channel in range(self.channel_count):
                    y = yield
                    segment[channel].append(y)
            for i in range(self.channel_count):
                result, filter_prev_state[i] = self.segmentPipeline(segment[i], filter_prev_state[i])
                coordinates[i].extend(result)
        ffts = []
        for i in range(self.channel_count):
            ffts.append(self.signalPipeline(coordinates[i]))
        for i in range(len(ffts[0])):
            summ = 0
            for j in range(self.channel_count):
                summ += ffts[j][i]
            average.append(summ/self.channel_count)
        yield self.normaliseSpectrum(average)
        while True:
            for _ in range(self.length/self.step):
                segment = [[] for _ in range(self.channel_count)]
                for j in range(self.step):
                    for channel in range(self.channel_count):
                        y = yield
                        segment[channel].append(y)
                for i in range(self.channel_count):
                    result, filter_prev_state[i] = self.segmentPipeline(segment[i], filter_prev_state[i])
                    coordinates[i].extend(result)
                    del coordinates[i][:self.step]
                ffts = []
                for i in range(self.channel_count):
                    ffts.append(self.signalPipeline(coordinates[i]))
                for i in range(len(ffts[0])):
                    summ = 0
                    for j in range(self.channel_count):
                        summ += ffts[j][i]
                    average[i] = summ/self.channel_count
                yield self.normaliseSpectrum(average)
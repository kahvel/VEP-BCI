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
        self.window = False
        self.normalise = False
        self.filter = False
        self.start_deleting = lambda x: True
        self.initial_packets = []

    def setInitSignal(self, min_packet, max_packet, averages, initial_packets, prev_packets):
        self.initial_packets = initial_packets

    def signalPipeline(self, coordinates):
        detrended_signal = scipy.signal.detrend(coordinates)
        filtered_signal = self.filterSignal(detrended_signal)
        self.prev_filter = self.filterPrevState(filtered_signal)
        windowed_signal = self.windowSignal(filtered_signal, self.window_function)
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        # normalised_spectrum = self.normaliseSpectrum(amplitude_spectrum)
        return amplitude_spectrum

    def windowSignal(self, signal, window):
        if self.window:
            return signal*window
        else:
            return signal

    def filterSignal(self, signal):
        if self.filter:
            if self.prev_filter is None:
                return scipy.signal.lfilter(self.filter_coefficients, 1.0, signal)
            else:
                result, self.prev_filter = scipy.signal.lfilter(self.filter_coefficients, 1.0, signal, zi=self.prev_filter)
                return result
        else:
            return signal

    def filterInitState(self, index):
        if self.filter:
            return scipy.signal.lfiltic(1.0, self.filter_coefficients, [0])
            # return scipy.signal.lfiltic(1.0, self.filter_coefficients, self.initial_packets[index])
        else:
            return None

    def normaliseSpectrum(self, fft):
        if self.normalise:
            return fft/sum(fft)
        else:
            return np.log10(fft)

    def filterPrevState(self, filtered_signal):  # We calculate prev filter state from signal[:self.step], because
                                                 # we save other values for next FFT (and also for next filtering)
        if self.filter:
            return scipy.signal.lfiltic(1.0, self.filter_coefficients, filtered_signal[:self.step])
        else:
            return None

    def setOptions(self, options_textboxes, variables):
        window_var = variables["Window"].get()
        if window_var == "None":
            self.window = False
        else:
            self.window = True
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
        self.filter = False
        self.filter_coefficients = []
        if variables["Filter"].get() == 1:
            self.filter = True
            low = options_textboxes["Low"].get()
            high = options_textboxes["High"].get()
            time_phase = int(options_textboxes["Taps"].get())
            if high != "" and low != "":
                low = float(low)
                high = float(high)
                self.filter_coefficients = scipy.signal.firwin(time_phase, [low/64.0, high/64.0], pass_zero=False, window="hanning")
            elif low != "":
                low = float(low)
                self.filter_coefficients = scipy.signal.firwin(time_phase, low/64.0)
            elif high != "":
                high = float(high)
                self.filter_coefficients = scipy.signal.firwin(time_phase, high/64.0, pass_zero=False)
            else:
                print "Insert high and/or low value"
                self.filter = False
        self.normalise = False
        if variables["Norm"].get() == 1:
            self.normalise = True

    def setup(self, options_textboxes, variables, sensor_names, freq_points):
        self.freq_points = freq_points
        self.length = int(options_textboxes["Length"].get())
        self.step = int(options_textboxes["Step"].get())
        self.setOptions(options_textboxes, variables)
        self.sensor_names = sensor_names
        self.channel_count = len(sensor_names)
        self.setPlotCount()
        self.generators = []
        for i in range(self.plot_count):
            self.generators.append(self.generator(i, self.start_deleting))
            self.generators[i].send(None)

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
        ret = self.generators[0].send(packet.sensors[self.sensor_names[0]]["value"])
        for i in range(1, self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])
        return ret

    def coordinates_generator(self, index):
        yield
        coordinates = self.initial_packets[index][:]
        self.prev_filter = self.filterInitState(index)
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
        ret = self.generators[0].send(packet.sensors[self.sensor_names[0]]["value"])
        for i in range(1, self.channel_count):
            self.generators[0].send(packet.sensors[self.sensor_names[i]]["value"])
        return ret

    def coordinates_generator(self, index):
        average = [0 for _ in range(self.length//2+1)]
        yield
        coordinates = [self.initial_packets[i][:] for i in range(self.channel_count)]
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
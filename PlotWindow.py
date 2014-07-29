__author__ = 'Anti'
import Tkinter
import MyWindows
import numpy as np
import scipy.signal


class PlotWindow(MyWindows.ToplevelWindow):
    def __init__(self, title):
        MyWindows.ToplevelWindow.__init__(self, title, 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.continue_generating = True
        self.canvas.pack()
        self.plot_count = 0
        self.channel_count = 0
        self.sensor_names = []
        self.generators = []
        self.plot_windows = {}
        self.length = None
        self.step = None
        self.window_length = 512
        self.window_height = 512
        self.window_function = None
        self.filter = False
        self.filter_coefficients = []
        self.normalise = False
        self.averages = []
        self.min_packet = []
        self.max_packet = []
        self.initial_packets = []
        self.window = False
        self.prev_filter = None

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

    def setup(self, options_textboxes, variables, sensor_names):
        self.length = int(options_textboxes["Length"].get())
        self.step = int(options_textboxes["Step"].get())
        self.setOptions(options_textboxes, variables)
        self.sensor_names = sensor_names
        self.channel_count = len(sensor_names)
        self.setPlotCount()
        self.generators = []
        for i in range(self.plot_count):
            self.generators.append(self.plot_generator(i, self.start_deleting))
            self.generators[i].send(None)

    def plot_generator(self, index, start_deleting):
        coordinates_generator = self.coordinates_generator(index)
        try:
            lines = [self.canvas.create_line(0, 0, 0, 0)]
            packet_count = 0
            delete = False
            coordinates_generator.send(None)
            while True:
                y = yield
                avg = coordinates_generator.send(y)
                if avg is not None:
                    scaled_avg = self.scale(avg, index, packet_count)
                    lines.append(self.canvas.create_line(scaled_avg))
                    coordinates_generator.next()
                    if start_deleting(packet_count):
                        packet_count = 0
                        delete = True
                    if delete:
                        self.canvas.delete(lines[0])
                        del lines[0]
                packet_count += 1
        finally:
            print "Closing generator"
            coordinates_generator.close()


class MultiplePlotWindow(PlotWindow):
    def __init__(self, title):
        PlotWindow.__init__(self, title)

    def setPlotCount(self):
        self.plot_count = self.channel_count


class SinglePlotWindow(PlotWindow):
    def __init__(self, title):
        PlotWindow.__init__(self, title)

    def setPlotCount(self):
        self.plot_count = 1
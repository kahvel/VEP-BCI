__author__ = 'Anti'
import MyWindows
import numpy as np
import scipy.signal


class ControllableWindow(MyWindows.ToplevelWindow):
    def __init__(self, title, width, height):
        MyWindows.ToplevelWindow.__init__(self, title, width, height)
        self.window_width = width
        self.window_height = height
        self.channel_count = 0
        self.plot_count = 0
        self.sensor_names = []
        self.generators = []
        self.continue_generating = True
        self.length = 512
        self.step = 32
        self.window_function = 1
        self.headset_freq = 128
        self.window = False
        self.normalise = False
        self.filter = False
        self.init_coordinates = []
        self.averages = []
        self.filter_coefficients = []
        self.filter_prev_state = None

    def windowSignal(self, signal, window):
        if self.window:
            return signal*window
        else:
            return signal

    def filterSignal(self, signal):
        if self.filter:
            if self.filter_prev_state is None:
                return scipy.signal.lfilter(self.filter_coefficients, 1.0, signal)
            else:
                result, self.filter_prev_state = scipy.signal.lfilter(self.filter_coefficients, 1.0, signal, zi=self.filter_prev_state)
                return result
        else:
            return signal

    def filterPrevState(self, prev_coordinates):
        if self.filter:
            return scipy.signal.lfiltic(1.0, self.filter_coefficients, prev_coordinates)
        else:
            return None

    def setWindow(self, options_textboxes, variables):
        window_var = variables["Window"].get()
        if window_var == "None":
            self.window = False
            self.window_function = None
        else:
            self.window = True
            if window_var == "hanning":
                self.window_function = np.hanning(self.length)
            elif window_var == "hamming":
                self.window_function = np.hamming(self.length)
            elif window_var == "blackman":
                self.window_function = np.blackman(self.length)
            elif window_var == "kaiser":
                self.window_function = np.kaiser(self.length, float(options_textboxes["Arg"].get()))
            elif window_var == "bartlett":
                self.window_function = np.bartlett(self.length)

    def setFilter(self, options_textboxes, variables):
        self.filter = False
        self.filter_coefficients = []
        if variables["Filter"].get() == 1:
            self.filter = True
            to_value = options_textboxes["To"].get()
            from_value = options_textboxes["From"].get()
            num_taps = int(options_textboxes["Taps"].get())
            nyq = self.headset_freq/2.0
            if from_value != "" and to_value != "":
                to_value = float(to_value)
                from_value = float(from_value)
                self.filter_coefficients = scipy.signal.firwin(num_taps, [from_value/nyq, to_value/nyq], pass_zero=False)
            elif to_value != "":
                to_value = float(to_value)
                self.filter_coefficients = scipy.signal.firwin(num_taps, to_value/nyq)
            elif from_value != "":
                from_value = float(from_value)
                self.filter_coefficients = scipy.signal.firwin(num_taps, from_value/nyq, pass_zero=False)
            else:
                print "Insert from and/or to value"
                self.filter = False

    def setNormalisation(self, variables):
        self.normalise = False
        if variables["Norm"].get() == 1:
            self.normalise = True

    def setOptions(self, options_textboxes, variables):
        self.setWindow(options_textboxes, variables)
        self.setFilter(options_textboxes, variables)
        self.setNormalisation(variables)

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
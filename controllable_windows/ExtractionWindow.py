__author__ = 'Anti'

from controllable_windows import ControllableWindow
import Tkinter
import ScrolledText


class ExtractionWindow(ControllableWindow.ControllableWindow):
    def __init__(self, title):
        ControllableWindow.ControllableWindow.__init__(self, title, 525, 200)
        self.canvas = ScrolledText.ScrolledText(self)
        self.canvas.pack()
        self.freq_points = None
        self.freq_indexes = None
        self.recorded_signals = None
        self.connection = None
        self.headset_freq = 128

    def resetCanvas(self):
        self.canvas.insert(Tkinter.END, "Starting\n")

    def setup(self, options, sensor_names, window_function, filter_coefficients, freq_points=None, recorded_signals=None, connection=None):
        self.freq_points = freq_points
        self.freq_indexes = []
        self.recorded_signals = recorded_signals
        self.sensor_names = sensor_names
        self.connection = connection
        ControllableWindow.ControllableWindow.setup(self, options, sensor_names, window_function, filter_coefficients)
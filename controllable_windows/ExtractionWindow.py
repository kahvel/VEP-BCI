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
        self.connection = None
        self.headset_freq = 128

    def resetCanvas(self):
        self.canvas.insert(Tkinter.END, "Starting\n")

    def generator(self, index):
        raise NotImplementedError("generator not implemented")

    def getGenerator(self, index):
        return self.generator(index)

    def setup(self, options, sensor_names, window_function, filter_coefficients,
              freq_points=None, connection=None):
        self.freq_points = freq_points
        self.sensor_names = sensor_names
        self.connection = connection
        ControllableWindow.ControllableWindow.setup(self, options, sensor_names, window_function, filter_coefficients)
__author__ = 'Anti'
import SNRExtraction
import ControlWindow


class Window(ControlWindow.ControlWindow):
    def __init__(self, connection, sensor_names):
        self.window_group_names = ["SNR"]
        self.window_names = ["SNR", "SumSNR"]
        self.button_names = ["", "Sum"]
        self.files = [SNRExtraction]
        ControlWindow.ControlWindow.__init__(self, "Extraction control", 320, 370, sensor_names)
        self.connection = connection
        self.freq_points = None
        self.recorded_signals = None
        self.myMainloop()

    def reset(self, windows, key, sensor_names):
        window = windows[key]
        if window is not None:
            window.resetCanvas()
            self.closeGenerators(window.generators)
            window.continue_generating = True
            window.setup(self.options, sensor_names, self.window_function, self.filter_coefficients, self.freq_points, self.recorded_signals, self.connection)

    def start(self):
        self.freq_points = self.connection.recv()
        self.recorded_signals = self.connection.recv()
        ControlWindow.ControlWindow.start(self)

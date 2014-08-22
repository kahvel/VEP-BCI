__author__ = 'Anti'

from control_windows import ControlWindow
from main_logic import PSDAExtraction, CCAExtraction, CCAPSDAExtraction


class Window(ControlWindow.ControlWindow):
    def __init__(self, connection, args):
        self.window_group_names = ["PSDA", "CCA", "CCA+PSDA"]
        self.window_names = ["Multiple", "Single"]
        self.button_names = ["", "Sum"]
        self.files = [PSDAExtraction, CCAExtraction, CCAPSDAExtraction]
        ControlWindow.ControlWindow.__init__(self, "Extraction control", 320, 370, args)
        self.connection = connection
        self.freq_points = None
        self.recorded_signals = None
        self.results = []
        self.myMainloop()

    def reset(self, windows, group_name, name, sensor_names):
        window = windows[group_name][name]
        if window is not None:
            window.resetCanvas()
            self.closeGenerators(window.generators)
            window.continue_generating = True
            window.setup(self.options, sensor_names, self.window_function, self.filter_coefficients,
                         self.freq_points, self.recorded_signals, self.connection)

    def start(self):
        self.freq_points = self.connection.recv()
        self.recorded_signals = self.connection.recv()
        message = ControlWindow.ControlWindow.start(self)
        return message

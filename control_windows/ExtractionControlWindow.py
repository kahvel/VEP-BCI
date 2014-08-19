__author__ = 'Anti'

from control_windows import ControlWindow
from main_logic import PSDAExtraction, CCAExtraction, CCAPSDAExtraction
from sklearn.metrics import confusion_matrix


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
        self.current_target = None
        self.result = None
        self.results = []
        self.myMainloop()

    def reset(self, windows, group_name, name, sensor_names):
        window = windows[group_name][name]
        if window is not None:
            self.result = {freq: 0 for freq in self.freq_points}
            window.resetCanvas()
            self.closeGenerators(window.generators)
            window.continue_generating = True
            window.setup(self.options, sensor_names, self.window_function, self.filter_coefficients,
                         self.freq_points, self.recorded_signals, self.connection, self.current_target,
                         self.result)

    def start(self):
        self.freq_points = self.connection.recv()
        self.recorded_signals = self.connection.recv()
        self.current_target = self.connection.recv()
        ControlWindow.ControlWindow.start(self)
        if self.current_target != 0:
            self.results.append((self.freq_points[self.current_target-1], self.result))
        else:
            self.results.append((0, self.result))
        print self.results
        # for result in self.results:
        #     detected_freq = []
        #     freqs = []
        #     for key in result[1]:
        #         freqs.append(float(key))
        #         detected_freq.extend([float(key) for _ in range(result[1][key])])
        #     actual_freq = [float(result[0]) for _ in range(len(detected_freq))]
        #     print freqs, actual_freq, detected_freq
        #     print confusion_matrix(actual_freq, detected_freq, labels=freqs)  # ValueError: Can't handle mix of binary and continuous

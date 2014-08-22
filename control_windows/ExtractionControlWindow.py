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
        message = ControlWindow.ControlWindow.start(self)
        if self.current_target != 0:
            self.results.append((self.freq_points[self.current_target-1], self.result))
        else:
            self.results.append((0, self.result))
        matrix_data = {}
        for result in self.results:
            detected_freq = []
            freqs = []
            if result[1] is not None:
                for key in sorted(result[1]):
                    freqs.append(str(key))
                    detected_freq.extend([str(key) for _ in range(result[1][key])])
                actual_freq = [str(result[0]) for _ in range(len(detected_freq))]
                str_freq = str(freqs)
                if str_freq in matrix_data:
                    matrix_data[str_freq][0].extend(actual_freq)
                    matrix_data[str_freq][1].extend(detected_freq)
                else:
                    matrix_data[str_freq] = []
                    matrix_data[str_freq].append(actual_freq)
                    matrix_data[str_freq].append(detected_freq)
                    matrix_data[str_freq].append(freqs)
        for key in matrix_data:
            print "Confusion matrix"
            print "Frequencies:", matrix_data[key][2]
            print confusion_matrix(matrix_data[key][0], matrix_data[key][1], labels=matrix_data[key][2])
        return message

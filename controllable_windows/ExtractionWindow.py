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
        # for packet in self.recorded_signals:
        #     self.sendPacket(packet, )
        # coordinates_generator = self.getCoordGenerator()
        # coordinates_generator.send(None)
        # processed_signals = []
        # for signal in self.recorded_signals:
        #     if signal is not None:
        #         processed_signals.append([])
        #         for packet in signal:
        #             for i in range(len(self.sensor_names)):
        #                 coordinates = coordinates_generator.send(float(packet.sensors[self.sensor_names[i]]["value"]))
        #                 if coordinates is not None:
        #                     processed_signals[-1].extend(coordinates)
        #     else:
        #         processed_signals.append(None)
        # print processed_signals
        return self.generator(index)

    def setup(self, options, sensor_names, window_function, filter_coefficients,
              freq_points=None, connection=None):
        self.freq_points = freq_points
        self.sensor_names = sensor_names
        self.connection = connection
        ControllableWindow.ControllableWindow.setup(self, options, sensor_names, window_function, filter_coefficients)
        # generators = []
        #
        # for i in range(self.gen_count):
        #     generators.append(self.getGenerator(i))
        #     generators[i].send(None)
        # for packet in self.recorded_signals:
        #     self.sendPacket(packet, generators, self.sensor_names)
        # results = []

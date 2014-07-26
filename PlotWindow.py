__author__ = 'Anti'
import Tkinter
import MyWindows
import numpy as np


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

    def setOptions(self, window_var, options_textboxes):
        self.length = int(options_textboxes["Length"].get())
        self.step = int(options_textboxes["Step"].get())
        window_var = window_var.get()
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
        elif window_var == "None":
            self.window_function = np.array([1 for _ in range(self.length)])

    def setup(self, checkbox_values, sensor_names):
        self.channel_count = 0
        self.sensor_names = []
        self.generators = []
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.sensor_names.append(sensor_names[i])
                self.channel_count += 1
        if self.channel_count == 0:
            self.continue_generating = False
            print "No channels chosen"
            return
        self.setPlotCount()
        for i in range(self.plot_count):
            self.generators.append(self.getGenerator(i))
            self.generators[i].send(None)

    def plot_generator(self, index, start_deleting):
        coordinates_generator = self.coordinates_generator()
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
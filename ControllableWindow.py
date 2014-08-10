__author__ = 'Anti'
import MyWindows


class ControllableWindow(MyWindows.ToplevelWindow):
    def __init__(self, title, width, height):
        MyWindows.ToplevelWindow.__init__(self, title, width, height)
        self.window_width = width
        self.window_height = height
        self.channel_count = 0
        self.plot_count = 0
        self.generators = []
        self.continue_generating = True
        self.window_function = None
        self.filter_coefficients = None
        self.options = None

    # def getPlotCount(self, channel_count):  # implemented in SignalProcessing
    #     raise NotImplementedError("getPlotCount not implemented")

    def generator(self, index, start_deleting):
        raise NotImplementedError("generator not implemented")

    def startDeleting(self):
        raise NotImplementedError("startDeleting not implemented")

    def setup(self, options, sensor_names, window_function, filter_coefficients):
        self.window_function = window_function
        self.filter_coefficients = filter_coefficients
        self.options = options
        self.channel_count = len(sensor_names)
        self.plot_count = self.getPlotCount(self.channel_count)
        self.generators = []
        for i in range(self.plot_count):
            self.generators.append(self.generator(i, self.startDeleting()))
            self.generators[i].send(None)
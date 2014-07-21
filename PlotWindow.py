__author__ = 'Anti'
import Tkinter
import MyWindows


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

    def plot_generator(self, index, update_after, start_deleting):
        coordinates_generator = self.coordinates_generator()
        try:
            lines = [self.canvas.create_line(0, 0, 0, 0)]
            packet_count = 0
            delete = False
            coordinates_generator.send(None)
            while True:
                y = yield
                avg = coordinates_generator.send(y)
                if packet_count % update_after == 0 and packet_count != 0:
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